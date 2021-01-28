<script>
    import { call } from './../services/service.js';
    import * as utils from './../services/utils.js';
    import {
        viewsStore,
        activeViewStore,
        activeRecordIdStore,
        recordCreatedStore,
        searchFiltersStore,
        publish,
        getValue
    } from './../services/writables.js';
    import Field from './Field.svelte';

    let view = null;
    let visible = false;
    let fetchedRecords = [];
    let fieldsDescription = null;
    let fetching = false;
    let page = 1;
    let numberOfPages;
    let numberOfRecords;
    let pageSize = 80;
    let filters = [];
    let batchActions = [];
    let selectAllChecked;
    let selectedRecords = {};

    searchFiltersStore.subscribe((event) => {
        if(event){
            filters = event.filters;
            fetchedRecords = [];
            fetchRecords();
        }
    })

    activeViewStore.subscribe((event) => {
        if(event){
            let type = event.type;
            visible = type === "list" || type == "search";
        }
    });

    viewsStore.subscribe((event) => {
        if(event){
            fetchedRecords = [];
            filters = [];
            page = 1;
            fieldsDescription = null;
            let views = event.views;
            if(views != null && views["list"]){
                view = views["list"];
                fetchRecords();
            }
        }
    });

    recordCreatedStore.subscribe((event) => {
        if(event){
            fetchedRecords = [];
            fetchRecords();
        }
    })

    function openSearch() {
        publish({
            event: 'activeViewChanged',
            type: 'search'
        })
    }

	async function fetchRecords(){
        fetching = true;
        if(view){
            let fields = [];
            selectedRecords = {};
            for(let item of view.definition.structure){
                fields.push(item.field);
                if(item.related_fields){
                    for(let rf of item.related_fields){
                        fields.push(item.field + "." + rf.field);
                    }
                }
            }
            if(!fieldsDescription){
                fieldsDescription = await call(view.model, "get_fields_desc", [fields]);
            }
            if(batchActions.length === 0){
                call(view.model, "get_batch_actions").then(
                    (resp) => {
                        batchActions = resp;
                    }
                )
            }
            call(view.model, "read", [fields], {filters:filters,count:true}).then(
                (resp) => {
                    numberOfPages = Math.ceil(resp / pageSize);
                    numberOfRecords = resp;
                }
            )
            call(view.model, "read", [fields], {filters:filters,paginate:[page, pageSize]}).then(
                (resp) => {
                    fetchedRecords = resp;
                    fetching = false;
                    for(let record of fetchedRecords){
                        selectedRecords[record.id] = false;
                    }
                }
            );
        }
    };

    function changePage(change){
        page += change;
        if(page > numberOfPages){
            page = 1;
        }else if(page == 0){
            page = numberOfPages;
        }
        fetchRecords();
    }

    function gotoPage(toPage){
        page = toPage;
        fetchRecords();
    }

    function create(){
        publish({
            'event': 'activeViewChanged',
            'type': 'form'
        })
        publish({
            'event': 'activeRecordIdChanged',
            'id': null
        })
    }

    function viewEdit(recordId){
        if(!("form" in getValue(viewsStore).views)){
            return;
        }
        utils.updateHash({
            type: 'form',
            id: recordId
        })
        publish({
            'event': 'activeViewChanged',
            'type': 'form'
        })
        publish({
            'event': 'activeRecordIdChanged',
            'id': recordId
        })
    }

    function renderField(record, field){
        if(!(field in record)){
            return "";
        }
        if(record[field] === null){
            return "";
        }else{
            if(fieldsDescription[field].type === "foreignkey"){
                return record[field].name || record[field].id;
            }else if(fieldsDescription[field].type === "date"){
                return utils.renderDate(record[field]);
            }else{
                return record[field];
            }
        }
    }

    function onChangeSelectAll(){
        for(let id in selectedRecords){
            selectedRecords[id] = selectAllChecked;
        }
    }

    function getSelectedIds(){
        var ids = [];
        for(let id in selectedRecords){
            if(selectedRecords[id]){
                ids.push(parseInt(id));
            }
        }
        return ids;
    }

    function doBatchAction(method){
        var ids = getSelectedIds();
        call(view.model, method, [ids]).then(
            (resp) => {
                fetchedRecords = [];
                fetchRecords();
            }
        )
    }
</script>

<div hidden={!visible}>
    <div id="list_view_toolbar" class="row">
        <div class="col-md">
        {#if view && view.definition.create !== false}
            <button type="button" class="btn btn-primary mb-2" on:click={create}>
                Nuevo
            </button>
        {/if}
        {#if view && view.menu_view_name}
            <strong class="ml-2" style="font-size:30px">{view.menu_view_name}</strong>
        {/if}
        </div>
        <div class="col-md top-left-controls">
            {#if selectedRecords && getSelectedIds().length > 0 && batchActions.length > 0}
                <div class="dropdown">
                    <button class="btn btn-secondary dropdown-toggle" type="button" id="actionsDropdown" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                        Acciones
                    </button>
                    <div class="dropdown-menu" aria-labelledby="actionsDropdown">
                        {#each batchActions as action}
                        <button class="dropdown-item" type="button"
                            on:click={()=>{
                                if(action.confirm){
                                    if(confirm(action.confirm)){
                                        doBatchAction(action.method);
                                    }
                                }else{
                                    doBatchAction(action.method);
                                }
                            }}>{action.label}</button>
                        {/each}
                    </div>
                </div>
            {/if}
            <button type="button" on:click={openSearch}
                class="btn btn-outline-secondary">
                <img src="icons/search.svg" alt="Filtros" />
            </button>
            <button type="button"
                class="btn btn-secondary btn-sm"
                disabled={fetching || page==1}
                on:click={()=>gotoPage(1)}>
                &lt;&lt;
            </button>
            <button type="button"
                class="btn btn-secondary btn-sm"
                disabled={fetching || page==1}
                on:click={()=>changePage(-1)}>
                &lt;
            </button>
                {(1 + (page-1) * pageSize) || ''}
                -
                {Math.min(numberOfRecords, ((page * pageSize) || 0)) || ''}
                de
                {numberOfRecords || ''}
            <button type="button"
                class="btn btn-secondary btn-sm"
                disabled={fetching || page==numberOfPages}
                on:click={()=>changePage(1)}>
                &gt;
            </button>
            <button type="button"
                class="btn btn-secondary btn-sm"
                disabled={fetching || page==numberOfPages}
                on:click={()=>gotoPage(numberOfPages)}>
                &gt;&gt;
            </button>
        </div>
    </div>

    <table class="table table-sm">
        <thead class="thead-light">
            {#if fieldsDescription && view}
                <th>
                    <input type="checkbox" bind:checked={selectAllChecked}
                        on:change={onChangeSelectAll}/>
                </th>
                {#each view.definition.structure as item}
                    {#if item.field && item.field in fieldsDescription}
                        <th>{item.label || fieldsDescription[item.field].label}</th>
                    {:else}
                        <th></th>
                    {/if}
                {/each}
            {/if}
        </thead>
        <tbody>
            {#each fetchedRecords as record}
                <tr on:click={() => viewEdit(record.id)}>
                    <td>
                        <input type="checkbox" bind:checked={selectedRecords[record.id]}
                            on:click|stopPropagation/>
                    </td>
                    {#each view.definition.structure as item}
                        {#if item.field && fieldsDescription && item.field in fieldsDescription}
                            <td>
                                <Field
                                    type={fieldsDescription[item.field].type}
                                    edit={false}
                                    bind:value={record[item.field]}
                                    choices={fieldsDescription[item.field].options}
                                    password={item.password || false}
                                    model={fieldsDescription[item.field].model}
                                    relatedFields={item.related_fields}
                                    relatedFieldsDesc={fieldsDescription[item.field].related_fields}
                                    nolabel={true}
                                    viewtype={'list'}
                                />
                            </td>
                        {:else}
                            <td></td>
                        {/if}
                    {/each}
                </tr>
            {/each}
        </tbody>
    </table>
    {#if fetchedRecords.length === 0 && !fetching }
        <p>No se encontraron registros</p>
    {/if}
</div>

<style>
    table{
        border: 1px solid silver;
        background-color: white;
    }

    #list_view_toolbar {
        padding: 10px
    }
    table tr{
        cursor:pointer
    }
    tr td {
        padding-bottom: 0px;
    }
    .top-left-controls{
        align-items:center;
        justify-content:flex-end;
        display: flex;
    }
    .top-left-controls button {
        margin: 2px 2px 2px 2px;
    }
</style>