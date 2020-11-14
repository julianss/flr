<script>
    import { call } from './../services/service.js';
    import { requestReport } from './../services/report.js';
    import {
        viewsStore,
        activeViewStore,
        activeRecordIdStore,
        publish
    } from './../services/writables.js';
    import Field from './Field.svelte';

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
    let reports = [];
    let validations = [];

    activeViewStore.subscribe((event) => {
        if(event){
            let type = event.type;
            visible = type === "form";
            editMode = false;
            validations = [];
        }
    });

    viewsStore.subscribe((event) => {
        if(event){
            fieldsDescription = null;
            let views = event.views;
            if(views != null && views["form"]){
                view = views["form"];
                sections = [];
                onChanges = [];
                for(let k in view.definition){
                    for(let item of view.definition[k]){
                        if(item.field && item.onchange){
                            onChanges[item.field] = item.onchange;
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
                    fields.push(item.field);
                    if(item.related_fields){
                        for(let rf of item.related_fields){
                            fields.push(item.field + "." + rf.field);
                        }
                    }
                }
            }
            call(view.model, "get_fields_desc", [fields]).then(
                (resp) => {
                    fieldsDescription = resp;
                    if(recordId){
                        call(view.model, "read", [fields], {filters:[['id','=',recordId]]}).then(
                            (resp) => {
                                record = resp[0];
                                notDirty = JSON.parse(JSON.stringify(resp[0]));
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
        let fieldDesc = fieldsDescription[item.field];
        if (fieldDesc.required === true && !value){
            validations.push(item)
        }
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
            call(view.model, method, args, kwargs).then(
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
    }

</script>

<div hidden={!visible}>
    <div id="form_view_toolbar">
        <div class="col-md">
            <button type="button" class="btn btn-secondary mb-2" on:click={back}>
                ≡ Listado
            </button>
            {#if recordId && !editMode}
                <button type="button" class="btn btn-primary mb-2" on:click={create}>
                    Nuevo
                </button>
            {/if}
            {#if editMode}
                <button type="button" class="btn btn-primary mb-2" on:click={save}>
                    Guardar
                </button>
                <button type="button" class="btn btn-light mb-2" on:click={discard}>
                    Descartar
                </button>
            {/if}
            {#if !editMode}
                <button type="button" class="btn btn-primary mb-2" on:click={edit}>
                    Editar
                </button>
            {/if}
            {#if view}
                <strong class="ml-2" style="font-size:30px">{view.menu_view_name}</strong>
            {/if}
        </div>
        <div class="col-md top-left-buttons">
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
                    <div class="alert alert-danger" role="alert">
                        <strong>Required fields</strong><br>
                        {#each validations as item}
                            {item.label || fieldsDescription[item.field].label}<br>
                        {/each}
                    </div>
                {/if}
                {#each sections as section}
                    {#each view.definition[section] as item}
                        {#if item.field && item.field in fieldsDescription }
                            <div hidden={section != activeSection || item.invisible && record[item.invisible]}>
                                <Field
                                    type={fieldsDescription[item.field].type}
                                    label={item.label || fieldsDescription[item.field].label}
                                    edit={editMode}
                                    bind:value={record[item.field]}
                                    password={item.password || false}
                                    model={fieldsDescription[item.field].model}
                                    options={fieldsDescription[item.field].options}
                                    required={item.required || fieldsDescription[item.field].required}
                                    relatedFields={item.related_fields}
                                    relatedFieldsDesc={fieldsDescription[item.field].related_fields}
                                    on:change={()=>fieldChanged(item.field)}
                                    nolabel={item.nolabel || false}
                                    add={item.add}
                                    remove={item.remove}
                                    readonly={item.readonly || false}
                                />
                            </div>
                        {/if}
                    {/each}
                {/each}
            {/if}
        </div>
    </div>
</div>

<style>

    .validations :global(label::after){
        content:"*";
        color:red
    }
    .validations :global(input, select){
        background-color:seashell
    }
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