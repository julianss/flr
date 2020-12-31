<script>
    import { call } from './../services/service.js';
    import { requestReport } from './../services/report.js';
    import { updateHash } from './../services/utils.js';
    import {
        viewsStore,
        activeViewStore,
        activeRecordIdStore,
        publish
    } from './../services/writables.js';
    import Field from './Field.svelte';
    import ActionButton from './ActionButton.svelte';
    import Element from './Element.svelte';
    import { setContext } from 'svelte';

    let view = null;
    let sections = [];
    let activeSection = "default";
    let visible = false;
    let recordId;
    let record = null;
    let notDirty = null;
    let fieldsDescription = null;
    let editMode = false;
    let onChanges = {};
    let invisibles = {};
    let reports = [];
    let validations = [];
    let isWizard = false;


    activeViewStore.subscribe((event) => {
        if(event){
            let type = event.type;
            visible = type === "form";
            editMode = false;
            validations = [];
            refreshInvisibles();
        }
    });

    viewsStore.subscribe((event) => {
        if(event){
            fieldsDescription = null;
            let views = event.views;
            if(views != null && views["form"]){
                if (!views["list"]){
                    isWizard = true;
                }else{
                    isWizard = false;
                }
                view = views["form"];
                sections = [];
                onChanges = [];
                invisibles = [];
                for(let k in view.definition){
                    for(let item of view.definition[k]){
                        if(item.field && item.onchange){
                            onChanges[item.field] = item.onchange;
                            invisibles[item.field] = {condition: item.invisible, result: false};
                        }
                        if(item.field && item.invisible){
                            invisibles[item.field] = {condition: item.invisible, result: false};
                        }
                    }
                }
                for(let item of view.definition.structure){
                    if(item.section){
                        sections.push(item.section)
                    }
                }
                if(sections.length == 0){
                    sections.push("default");
                    activeSection = "default";
                    view.definition.default = view.definition.structure;
                }else{
                    activeSection = sections[0];
                }
            }
            call("FlrReport", "read", [["name"]], {filters:[["model","=",view.model]]}).then(
                (resp) => {
                    reports = resp;
                }
            )
        }
    })

    activeRecordIdStore.subscribe((event) => {
        if(event){
            let id = event.id;
            recordId = id;
            getRecord();
        }
    })

    function back(){
        updateHash({
            type: null,
            id: null
        })
        publish({
            'event': 'activeViewChanged',
            'type': 'list'
        })
    }

    function create(){
        publish({
            'event': 'activeRecordIdChanged',
            'id': null
        })
    }

    function getRecord(){
        if(view){
            let fields = [];
            for(let section of sections){
                for(let item of view.definition[section]){
                    if (item.field){
                        fields.push(item.field);
                        if(item.related_fields){
                            for(let rf of item.related_fields){
                                fields.push(item.field + "." + rf.field);
                            }
                        }
                    }
                }
            }
            call(view.model, "get_fields_desc", [fields]).then(
                (resp) => {
                    fieldsDescription = resp;
                    fieldsDescription["id"].required = false;
                    fieldsDescription["id"].readonly = true;
                    if(recordId){
                        call(view.model, "read", [fields], {filters:[['id','=',recordId]]}).then(
                            (resp) => {
                                record = resp[0];
                                notDirty = JSON.parse(JSON.stringify(resp[0]));
                                refreshInvisibles();
                            }
                        );
                    }else{
                        let blankRecord = {id: null};
                        for(let field in fieldsDescription){
                            blankRecord[field] = null;
                        }
                        call(view.model, "get_default").then(
                            (defaults) => {
                                for(let field in defaults){
                                    blankRecord[field] = defaults[field];
                                }
                                record = blankRecord;
                                notDirty = JSON.parse(JSON.stringify(blankRecord));
                                editMode = true;
                                refreshInvisibles();
                            }
                        )

                    }
                }
            );
        }
    }

    function getRecordDirtyPart(){
        let dirtyPart = {};
        for(let field in record){
            if(JSON.stringify(notDirty[field]) !== JSON.stringify(record[field])){
                dirtyPart[field] = record[field];
            }
        }
        dirtyPart.id = undefined;
        return dirtyPart;
    }

    function validate(item, value){
        if ('field' in item){
            let fieldDesc = fieldsDescription[item.field];
            if(fieldDesc){
                if (fieldDesc.required === true && !value){
                    validations.push(item)
                }
            }
        }
    }
    function resetValidations(){
        validations = []
    }

    function save(){
        let method;
        let args;
        let kwargs;
        validations = [];
        if(!record.id){
            record.id = undefined;
            method = "create";
            args = [];
            kwargs = record;
        }else{
            method = "update";
            args = [getRecordDirtyPart()];
            kwargs = {filters: [["id","=",record.id]]}
        }

        for(let section of sections){
            for(let item of view.definition[section]){
                validate(item, record[item.field])
            }
        }
        if (validations.length === 0){
            var promise = call(view.model, method, args, kwargs)
            promise.then(
                (resp) => {
                    if(!resp.error){
                        publish({
                            event: 'activeRecordIdChanged',
                            id: method=="create"?resp:record.id
                        })
                        publish({event: 'recordCreated'})
                        editMode = false;
                    }
                }
            )
            return promise;
        }
    }
    
    function edit(){
        editMode = true;
    }

    function discard(){
        editMode = false;
        record = notDirty;
        if(!recordId){
            back();
        }
    }

    function fieldChanged(field){
        if(onChanges[field]){
            call(view.model, onChanges[field], [record]).then(
                (resp) => {
                    if(resp["value"]){
                        for(let f in resp["value"]){
                            record[f] = resp["value"][f];
                        }
                        record = record;
                    }
                }
            )
        }
        refreshInvisibles();
    }

    function refreshInvisibles(){
        if(!record){
            return;
        }
        for(let field in invisibles){
            if(!invisibles[field].condition){
                invisibles[field].result = false;
            }else {
                let code = "return " + invisibles[field].condition;
                invisibles[field].result = new Function(code).call(record);
            }
        }
        invisibles = invisibles;
    }

    setContext('formViewFunctions', {
        'save': () => save()
    });

</script>

<div hidden={!visible}>
    <div id="form_view_toolbar">
        <div class="col-md">
            {#if !isWizard}
                <button type="button" class="btn btn-secondary mb-2" on:click={back}>
                    ≡ Listado
                </button>
                {#if recordId && !editMode}
                    <button type="button" class="btn btn-primary mb-2" on:click={create}>
                        Nuevo
                    </button>
                {/if}
            {/if}
            {#if editMode}
                <button type="button" class="btn btn-primary mb-2" on:click={save}>
                    Guardar
                </button>
                {#if !isWizard}
                    <button type="button" class="btn btn-light mb-2" on:click={discard}>
                        Descartar
                    </button>
                {/if}
            {/if}
            {#if !editMode}
                {#if !isWizard}
                    <button type="button" class="btn btn-primary mb-2" on:click={edit}>
                        Editar
                    </button>
                {/if}
            {/if}
            {#if view}
                <strong class="ml-2" style="font-size:30px">{view.menu_view_name}</strong>
            {/if}
        </div>
        <div class="col-md top-left-buttons">
            {#if view && record && record.id && view.definition.buttons}
                {#each view.definition.buttons as button}
                    <ActionButton
                        action={button.action}
                        text={button.text}
                        options={button.options}
                        model={view.model}
                        bind:record
                        view={this}
                    />
                {/each}
            {/if}
            {#if record && reports && record.id && reports.length>0}
                <div class="dropdown">
                    <button class="btn btn-secondary dropdown-toggle" type="button" id="actionsDropdown" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                        Imprimir
                    </button>
                    <div class="dropdown-menu dropdown-menu-right" aria-labelledby="actionsDropdown">
                        {#each reports as report}
                            <button class="dropdown-item" type="button"
                                on:click={()=>{
                                requestReport(report.name, [record.id])
                                }}>{report.name}</button>
                        {/each}
                    </div>
                </div>
            {/if}
        </div>
    </div>
    <div id="form_area_wrapper">
        <div id="form_area">
            {#if sections.length > 1}
                <div class="tabs">
                    <ul class="nav nav-tabs">
                        {#each sections as section}
                            <li class="nav-item">
                                <a
                                    class={section==activeSection?'nav-link active':'nav-link'}
                                    on:click={()=>activeSection=section}
                                    href="#">
                                    {section}
                                </a>
                            </li>
                        {/each}
                    </ul>
                </div>
            {/if}
            {#if view && fieldsDescription && record}
                {#if validations.length > 0}
                    <div class="alert alert-dismissible alert-danger" role="alert">
                        <button type="button" class="close" data-dismiss="alert"
                            on:click={resetValidations}>×</button>
                        <strong>Required fields</strong><br>
                        {#each validations as item}
                            {item.label || fieldsDescription[item.field].label}<br>
                        {/each}
                    </div>
                {/if}
                {#each sections as section}
                    {#each view.definition[section] as item}
                        {#if item.field && item.field in fieldsDescription }
                            <div hidden={section != activeSection || invisibles[item.field] && invisibles[item.field].result}>
                                <Field
                                    type={fieldsDescription[item.field].type}
                                    label={item.label || fieldsDescription[item.field].label}
                                    edit={editMode}
                                    bind:value={record[item.field]}
                                    password={item.password || false}
                                    viewpassword={item.viewpassword || false}
                                    model={fieldsDescription[item.field].model}
                                    choices={fieldsDescription[item.field].options}
                                    required={item.required || fieldsDescription[item.field].required}
                                    relatedFields={item.related_fields}
                                    relatedFieldsDesc={fieldsDescription[item.field].related_fields}
                                    on:change={()=>fieldChanged(item.field)}
                                    nolabel={item.nolabel || false}
                                    add={item.add}
                                    remove={item.remove}
                                    readonly={item.readonly || false}
                                    viewtype={'form'}
                                    options={item.options || {}}
                                />
                            </div>
                        {:else if item.tag}
                            <div>
                                <Element
                                    tag={item.tag}
                                    text={item.text}
                                />
                            </div>
                        {:else if item.button}
                            <ActionButton
                                action={item.button.action}
                                text={item.button.text}
                                options={item.button.options}
                                model={view.model}
                                bind:record
                            />
                        {/if}
                    {/each}
                {/each}
            {/if}
        </div>
    </div>
</div>

<style>
    .tabs {
        background-color:white;
        margin-bottom: 10px;
    }
    #form_view_toolbar {
        padding: 10px;
        display: flex
    }
    .top-left-buttons{
        align-items:center;
        justify-content:flex-end;
        display: flex;
    }
    .top-left-buttons button {
        margin: 2px 2px 2px 2px;
    }
    @media(min-width: 600px){
        #form_area {
            width: 80%;
            margin: auto;
            background-color: white;
            padding: 30px;
            position:relative;
            top:30px;
            box-shadow: 10px 0px 20px gray
        }
    }
    #form_area_wrapper {
        background: rgb(211,211,211,0.5);
        background: linear-gradient(180deg, rgba(211,211,211,1) 0%, rgba(211,211,211,1) 5%, rgba(255,255,255,0) 100%);
    }
</style>