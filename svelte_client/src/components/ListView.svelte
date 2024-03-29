<script>
    import { _ } from 'svelte-i18n';
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
    import ejs from './../services/ejs.min.js';
    import { getSrcWithToken } from './../services/files.js';
    import ExportView from './ExportView.svelte';

    let view = null;
    let model;
    let fields;
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
    let cardViewTemplate = false;
    let cardViewEnabled = false;
    let groupImportExportButton;

    searchFiltersStore.subscribe((event) => {
        if(event){
            filters = event.filters;
            fetchedRecords = [];
            gotoPage(1);
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
            call('FlrUser', 'groups_check_any', ['flrgroup_export_import']).then(
                (resp)=>{
                    groupImportExportButton = resp;
                }
            )
            fetchedRecords = [];
            filters = [];
            page = 1;
            fieldsDescription = null;
            selectAllChecked = false;
            let views = event.views;
            if(views != null && views["list"]){
                view = views["list"];
                model = view.model;
                cardViewTemplate = view.card_view_template;
                cardViewEnabled = false;
                if(cardViewTemplate && view.card_view_first){
                    cardViewEnabled = true;
                }
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
            let fields_ = [];
            selectedRecords = {};
            for(let item of view.definition.structure){
                fields_.push(item.field);
                if(item.options && item.options.related_fields){
                    for(let rf of item.options.related_fields){
                        fields_.push(item.field + "." + rf.field);
                    }
                }
            }
            fields = fields_;
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

    function openExportView() {
        document.getElementById("button-modal-export").click();
    }

</script>

<div hidden={!visible}>
    <button id="button-modal-export" style="display:none" type="button" data-bs-toggle="modal"
        data-bs-target="#export-view-modal"></button>
    <div id="export-view-modal" class="modal fade" tabindex="-1" role="dialog"
        aria-labelledby="exportView" aria-hidden="true">
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">{$_('export_view.title')}</h5>
                    <button type="button" class="close" data-bs-dismiss="modal" aria-label="Close">
                    <span aria-hidden="true">&times;</span>
                    </button>
                </div>
                <div class="modal-body">
                    <ExportView
                        on:success={fetchRecords}
                        model={model}
                        selectedFields={fields}
                        filters={filters}
                        page={page}
                        pageSize={pageSize}
                        selectedRecords={selectedRecords}/>
                </div>
            </div>
        </div>
    </div>
    <div id="list_view_toolbar" class="row">
        <div class="col-md">
        {#if view && view.definition.create !== false}
            <button type="button" class="btn btn-primary mb-2" on:click={create}>
                <img src="icons/plus.svg" style="filter:invert(1)" title={$_('list_view.new')} alt={$_('list_view.new')}>
            </button>
        {/if}
        {#if view && view.menu_view_name}
            <strong class="ml-2" style="margin-left:10px;font-size:30px">{view.menu_view_name}</strong>
        {/if}
        </div>
        <div class="col-md top-left-controls">
            {#if selectedRecords && getSelectedIds().length > 0 && batchActions.length > 0}
                <div class="dropdown">
                    <button class="btn btn-secondary dropdown-toggle" href="#" id="actionsDropdown" role="button" data-bs-toggle="dropdown" aria-expanded="false"> 
                        <img src="icons/three-dots.svg" style="filter:invert(1)" title={$_('list_view.actions')} alt={$_('list_view.actions')}>
                    </button>
                    <ul class="dropdown-menu" aria-labelledby="actionsDropdown">
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
                    </ul>
                </div>
            {/if}
            {#if groupImportExportButton}
                <button on:click={openExportView} class="btn btn-secondary" type="button">
                    <img src="icons/save.svg" style="filter:invert(1)" title={$_('list_view.actions')} alt={$_('list_view.actions')}/>
                </button>
            {/if}
            {#if view && cardViewTemplate && !cardViewEnabled}
                <button type="button" on:click={()=>{cardViewEnabled=true}}
                    class="btn btn-secondary">
                    <img src="icons/grid-3x3-gap-fill.svg" style="filter:invert(1)" title={$_('list_view.card')} alt={$_('list_view.card')}/>
                </button>
            {/if}
            {#if cardViewEnabled}
                <button type="button" on:click={()=>{cardViewEnabled=false}}
                    class="btn btn-secondary">
                    <img src="icons/list.svg" style="filter:invert(1)" title={$_('list_view.list')} alt={$_('list_view.list')}/>
                </button>
            {/if}
            <button type="button" on:click={openSearch}
                class="btn btn-secondary">
                <img src="icons/search.svg" style="filter:invert(1)" title={$_('list_view.search')} alt={$_('list_view.search')}/>
            </button>
            <button type="button"
                class="btn btn-secondary btn-sm"
                disabled={fetching || page==1}
                on:click={()=>gotoPage(1)}>
                <img src="icons/chevron-double-left.svg" style="filter:invert(1)" title={$_('list_view.first')} alt="{$_('list_view.first')}">
            </button>
            <button type="button"
                class="btn btn-secondary btn-sm"
                disabled={fetching || page==1}
                on:click={()=>changePage(-1)}>
                <img src="icons/chevron-left.svg" style="filter:invert(1)" title="{$_('list_view.previous')}" alt="{$_('list_view.previous')}">
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
                <img src="icons/chevron-right.svg" style="filter:invert(1)" title="{$_('list_view.next')}" alt="{$_('list_view.next')}">
            </button>
            <button type="button"
                class="btn btn-secondary btn-sm"
                disabled={fetching || page==numberOfPages}
                on:click={()=>gotoPage(numberOfPages)}>
                <img src="icons/chevron-double-right.svg" style="filter:invert(1)" title="{$_('list_view.last')}" alt="{$_('list_view.last')}">
            </button>
        </div>
    </div>

    {#if !cardViewEnabled}
        <div class="tableFixHead">
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
                                            label={item.label || fieldsDescription[item.field].label}
                                            edit={false}
                                            bind:value={record[item.field]}
                                            choices={fieldsDescription[item.field].options}
                                            required={false}
                                            model={fieldsDescription[item.field].model}
                                            model_name_field={fieldsDescription[item.field].model_name_field}
                                            relatedFieldsDesc={fieldsDescription[item.field].related_fields}
                                            nolabel={true}
                                            readonly={false}
                                            filters={[]}
                                            viewtype={'list'}
                                            options={item.options || {}}
                                        />
                                    </td>
                                {:else}
                                    <td></td>
                                {/if}
                            {/each}
                        </tr>
                    {/each}
                </tbody>
                <tfoot>
                    {#if view}
                        <tr>
                            <td></td>
                            {#each view.definition.structure as item}
                                {#if item.field && fieldsDescription && item.field in fieldsDescription && item.options && 'sum' in item.options}
                                    <td>{fetchedRecords.reduce((a, b) => a + (b[item.field] || 0), 0)}</td>
                                {:else}
                                    <td></td>
                                {/if}
                            {/each}
                        </tr>
                    {/if}
                </tfoot>
            </table>
        </div>
    {:else}
        <div class="card-view-container">
            {#each fetchedRecords as record}
                <div class="card-view-wrapper" on:click={() => viewEdit(record.id)}>
                    {@html ejs.render(cardViewTemplate, {...record, getUrl: getSrcWithToken})}
                </div>
            {/each}
        </div>
    {/if}
    {#if fetchedRecords.length === 0 && !fetching }
        <p>{$_('list_view.no_records_found')}</p>
    {/if}
</div>

<style>
    .tableFixHead thead th {
        position: sticky;
        top: 0;
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
    .card-view-wrapper {
        margin: 5px 5px 5px 5px
    }
    .card-view-container {
        display: flex;
        flex-wrap: wrap;
        justify-content: center;
        cursor: pointer
    }
</style>