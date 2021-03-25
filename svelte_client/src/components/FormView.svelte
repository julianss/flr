<script>
    import { call } from './../services/service.js';
    import { requestReport } from './../services/report.js';
    import { updateHash, getUniqueId } from './../services/utils.js';
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
    let readonlys = {};
    let requireds = {}
    let reports = [];
    let validations = {
        'required': [],
        'others': []
    };
    let isWizard = false;
    let showSaveButton = false;
    let listViewExists = false;
    let fetchingRecord = false;
    let disabled = false;

    activeViewStore.subscribe((event) => {
        if(event){
            let type = event.type;
            visible = type === "form";
            editMode = false;
            validations = {
                'required': [],
                'others': []
            };
            refreshModifiers();
        }
    });

    viewsStore.subscribe((event) => {
        if(event){
            fieldsDescription = null;
            let views = event.views;
            if(views != null && views["form"]){
                listViewExists = "list" in views;
                view = views["form"];
                isWizard = view.wizard || false
                showSaveButton = view.showSaveButton || false;
                sections = [];
                onChanges = {};
                invisibles = {};
                readonlys = {};
                requireds = {};
                for(let k in view.definition){
                    if (typeof view.definition[k] === 'string'){
                        var uid = getUniqueId();
                        invisibles[uid] = {condition: view.definition[k], result: false};
                        view.definition[k] = {id:uid}
                    }else if (typeof view.definition[k] !== 'boolean'){
                        for(let item of view.definition[k]){
                            if(item.field && item.onchange){
                                onChanges[item.field] = item.onchange;
                            }
                            let modifiers = [
                                ["invisible", invisibles],
                                ["readonly", readonlys],
                                ["required", requireds],
                            ];
                            for(let pair of modifiers){
                                let modifier = pair[0];
                                let modifierState = pair[1];
                                if(modifier in item){
                                    var uid;
                                    if(item.id){
                                        uid = item.id;
                                    }else if(item.section){
                                        uid = item.section;
                                    }else if(item.field){
                                        uid = item.field;
                                    }else{
                                        uid = getUniqueId();
                                    }
                                    let initialVal = false;
                                    if(typeof(item[modifier]) == "boolean"){
                                        initialVal = item[modifier];
                                    }
                                    modifierState[uid] = {condition: item[modifier], result: initialVal};
                                    item.id = uid;
                                }
                            }
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
            fetchingRecord = true;
            let fields = [];
            let options = {'name_field': {}}
            for(let section of sections){
                for(let item of view.definition[section]){
                    if (item.field){
                        fields.push(item.field);
                        if (item.options && item.options.name_field){
                            options.name_field[item.field] = item.options.name_field
                        }
                        if(item.options && item.options.related_fields){
                            for(let rf of item.options.related_fields){
                                fields.push(item.field + "." + rf.field);
                            }
                        }
                    }
                }
            }
            call(view.model, "get_fields_desc", [fields]).then(
                (resp) => {
                    fieldsDescription = resp;
                    if(recordId){
                        call(view.model, "read", [fields], {filters:[['id','=',recordId]], options: options}).then(
                            (resp) => {
                                record = resp[0];
                                notDirty = JSON.parse(JSON.stringify(resp[0]));
                                refreshModifiers();
                                fetchingRecord = false;
                            }
                        );
                    }else{
                        let blankRecord = {id: null};
                        for(let field in fieldsDescription){
                            blankRecord[field] = null;
                        }
                        call(view.model, "get_default").then(
                            (defaults) => {
                                if(defaults.$error){
                                    fieldsDescription = null;
                                    fetchingRecord = false;
                                }else{
                                    for(let field in defaults){
                                        blankRecord[field] = defaults[field];
                                    }
                                    record = blankRecord;
                                    notDirty = JSON.parse(JSON.stringify(blankRecord));
                                    editMode = true;
                                    refreshModifiers();
                                    fetchingRecord = false;
                                }
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

    function validate(item, value, section){
        if ('field' in item){
            let fieldDesc = fieldsDescription[item.field];
            if(fieldDesc){
                if (fieldDesc.required === true && !value){
                    validations['required'].push(item)
                }
            }
            if (item.options && item.options.hasOwnProperty('minVal') && value < item.options.minVal){
                if (validations['others'].indexOf(item)===-1){
                  validations['others'].push(item);
                }
                for (var i in view.definition[section]){
                    if (view.definition[section][i] === item){
                        view.definition[section][i].options.minValError = true;
                    }
                }
            }else if (item.options && item.options.hasOwnProperty('maxVal') && value > item.options.maxVal){
                if (validations['others'].indexOf(item)===-1){
                    validations['others'].push(item);
                }
                for (var i in view.definition[section]){
                    if (view.definition[section][i] === item){
                        view.definition[section][i].options.maxValError = true;
                    }
                }
            }
        }
    }
    function resetValidations(){
        validations = {
            'required': [],
            'others': []
        }
    }

    function save(event){
        if (event && !(event.detail === 1)){
            return
        }
        let method;
        let args;
        let kwargs;
        validations = {
            'required': [],
            'others': []
        };
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
                if(item.field){
                    validate(item, record[item.field], section)
                }
            }
        }
        var i = 0;
        for (var key in validations){
            i = i + validations[key].length
        }
        if (i === 0){
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
    function wrapFunctionSave(event){
        disabled = true;
        try {
            save(event)
        }
        finally {
            disabled = false;
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
        refreshModifiers();
    }

    function refreshModifiers(){
        if(!record){
            return;
        }
        if(!fieldsDescription){
            return;
        }
        for(let modifierState of [invisibles, readonlys, requireds]){
            for(let uid in modifierState){
                if(typeof(modifierState[uid].condition) == "boolean"){
                    modifierState[uid].result = modifierState[uid].condition;
                }else{
                    let code = "return " + modifierState[uid].condition;
                    modifierState[uid].result = new Function(code).call(record);
                }
                if (requireds === modifierState){
                    if (uid in modifierState && fieldsDescription && 'required' in fieldsDescription[uid]){
                        fieldsDescription[uid].required = modifierState[uid].result
                    }
                }
            }
        }
        invisibles = invisibles;
        readonlys = readonlys;
        requireds = requireds;
    }

    setContext('formViewFunctions', {
        'save': () => save()
    });


</script>

<div hidden={!visible}>
    <div id="form_view_toolbar">
        <div class="col-md">
            {#if isWizard}
                <button type="button" class="btn btn-secondary mb-2" on:click={()=>history.back()}>
                    <img src="icons/arrow-left.svg" style="filter:invert(1)" title="Regresar" alt="Regresar">
                </button>
            {/if}
            {#if !isWizard}
                {#if listViewExists}
                    <button type="button" class="btn btn-secondary mb-2" on:click={back}>
                        <img src="icons/arrow-left.svg" style="filter:invert(1)" title="Regresar" alt="Regresar">
                    </button>
                {/if}
                {#if view && view.definition.create !== false}
                    {#if recordId && !editMode}
                        <button type="button" class="btn btn-primary mb-2" on:click={create}>
                            <img src="icons/plus.svg" style="filter:invert(1)" title="Nuevo" alt="Nuevo">
                        </button>
                    {/if}
                {/if}
            {/if}
            {#if editMode && (!isWizard || showSaveButton)}
                <button type="button" class="btn btn-primary mb-2" on:click={wrapFunctionSave} disabled="{disabled}">
                    <img src="icons/check2.svg" style="filter:invert(1)" title="Guardar" alt="Guardar">
                </button>
                {#if !isWizard}
                    <button type="button" class="btn btn-outline-secondary mb-2" on:click={discard}>
                        <img src="icons/x.svg" title="Descartar" alt="Descartar">
                    </button>
                {/if}
            {/if}
            {#if view && view.definition.edit !== false}
                {#if !editMode}
                    {#if !isWizard}
                        <button hidden={view.definition.edit && view.definition.edit.hasOwnProperty('id') && view.definition.edit.id in invisibles && !invisibles[view.definition.edit.id].result}
                            type="button" class="btn btn-primary mb-2" on:click={edit}>
                            <img src="icons/pencil-square.svg" style="filter:invert(1)" title="Editar" alt="Editar">
                        </button>
                    {/if}
                {/if}
            {/if}
            {#if view}
                <strong class="ml-2" style="font-size:30px">{view.menu_view_name}</strong>
            {/if}
        </div>
        <div class="col-md top-left-buttons">
            {#if view && record && record.id && view.definition.buttons}
                {#each view.definition.buttons as button}
                    <div hidden={invisibles[button.id] && invisibles[button.id].result}>
                        <ActionButton
                            action={button.action}
                            text={button.text}
                            options={button.options}
                            model={view.model}
                            bind:record
                            view={this}
                        />
                    </div>
                {/each}
            {/if}
            {#if record && reports && record.id && reports.length>0}
                <div class="dropdown">
                    <button class="btn btn-secondary dropdown-toggle" type="button" id="actionsDropdown" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                        <img src="icons/download.svg" style="filter:invert(1)" title="Descargar" alt="Descargar">
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
                            <li class="nav-item" hidden={invisibles[section] && invisibles[section].result}>
                                <a
                                    class={section==activeSection?'nav-link active':'nav-link'}
                                    on:click={(e)=>{e.preventDefault();activeSection=section}}
                                    href="#">
                                    {section}
                                </a>
                            </li>
                        {/each}
                    </ul>
                </div>
            {/if}
            {#if view && fieldsDescription && record && (!fetchingRecord || recordId==record.id)}
                {#if validations['required'].length > 0 || validations['others'].length > 0}
                    <div class="alert alert-dismissible alert-danger" role="alert">
                        <button type="button" class="close" data-dismiss="alert"
                            on:click={resetValidations}>×</button>
                        {#if validations['required'].length > 0}
                            <strong>Required fields</strong><br>
                            {#each validations['required'] as item}
                                {item.label || fieldsDescription[item.field].label}<br>
                            {/each}
                        {/if}
                        {#if validations['others'].length > 0}
                            <strong>Fields has errors</strong><br>
                            {#each validations['others'] as item}
                                {item.label || fieldsDescription[item.field].label}<br>
                            {/each}
                        {/if}
                    </div>
                {/if}
                {#each sections as section}
                    <div class="fields-container">
                    {#each view.definition[section] as item}
                        {#if item.field && item.field in fieldsDescription }
                            <div class="field-wrapper" style="width:{(item.options && item.options.width) || '100%'}"
                                hidden={section != activeSection || invisibles[item.id] && invisibles[item.id].result}>
                                <Field
                                    type={fieldsDescription[item.field].type}
                                    label={item.label || fieldsDescription[item.field].label}
                                    edit={editMode}
                                    bind:value={record[item.field]}
                                    model={fieldsDescription[item.field].model}
                                    choices={fieldsDescription[item.field].options}
                                    required={
                                        (item.id in requireds) ?
                                        requireds[item.id].result : fieldsDescription[item.field].required
                                    }
                                    relatedFieldsDesc={fieldsDescription[item.field].related_fields}
                                    on:change={()=>fieldChanged(item.field)}
                                    nolabel={item.nolabel || false}
                                    readonly={
                                        (item.id in readonlys) ?
                                        readonlys[item.id].result : fieldsDescription[item.field].readonly || false
                                    }
                                    viewtype={'form'}
                                    options={item.options || {}}
                                />
                            </div>
                        {:else if item.tag}
                            <div hidden={section != activeSection || invisibles[item.id] && invisibles[item.id].result}>
                                <Element
                                    tag={item.tag}
                                    text={item.text}
                                />
                            </div>
                        {:else if item.button}
                            <div hidden={section != activeSection || invisibles[item.id] && invisibles[item.id].result}>
                                <ActionButton
                                    action={item.button.action}
                                    text={item.button.text}
                                    options={item.button.options}
                                    model={view.model}
                                    bind:record
                                />
                            </div>
                        {/if}
                    {/each}
                    </div>
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
    .fields-container {
        display:flex;
        width:100%;
        flex-wrap: wrap
    }
    .field-wrapper {
        padding-right: 10px;
        padding-left: 10px
    }
</style>
