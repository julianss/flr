<script>
    import { call } from './../services/service.js';
    import { 
        viewsStore,
        activeViewStore,
        activeRecordIdStore,
        recordCreatedStore,
        searchFiltersStore,
        publish,
        getValue
    } from './../services/writables.js';

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
            console.log(event);
            fetchedRecords = [];
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
            for(let item of view.definition.structure){
                fields.push(item.field);
            }
            if(!fieldsDescription){
                fieldsDescription = await call(view.model, "get_fields_desc", [fields]);
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
            if(fieldsDescription[field].type == "foreignkey"){
                return record[field].name || record[field].id;
            }else{
                return record[field];
            }
        }
    }
</script>

<div hidden={!visible}>
    <div id="list_view_toolbar" class="row">
        {#if view && view.definition.create !== false}
            <div class="col-md">
                <button type="button" class="btn btn-primary" on:click={create}>
                    Nuevo
                </button>
            </div>
        {/if}
        <div class="col-md" style="text-align:right">
            <button type="button"
                class="btn btn-secondary">
                <img src="icons/search.svg" alt="Filtros" on:click={openSearch}/>
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
                    {#each view.definition.structure as item}
                        {#if item.field && item.field in fieldsDescription}
                            <td>{renderField(record, item.field)}</td>
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
</style>