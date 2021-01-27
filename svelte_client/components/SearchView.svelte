<script>
    import { call } from './../services/service.js';
    import {
        viewsStore,
        activeViewStore,
        getValue,
        searchFiltersStore, 
        publish
    } from './../services/writables.js';
    import Field from './Field.svelte';
    import { createEventDispatcher } from 'svelte';
    const dispatch = createEventDispatcher();

    let fieldsDescription = null;
    let visible = false;
    let fields = [];
    let filters = [];
    let view;
    let selectedValues = {};
    let selectedValues2 = {};
    let selectedOperators = {};

    activeViewStore.subscribe((event) => {
        if(event){
            if(event.type === "search"){
                openModal();
            }
        }
    })

    viewsStore.subscribe((event) => {
        if(event){
            fieldsDescription = null;
            selectedOperators = {};
            selectedValues = {};
            let views = event.views;
            if(views != null && views["search"]){
                view = views["search"];
                for(let field of view.definition.fields){
                    fields.push(field.field);
                    selectedOperators[field] = null;
                    selectedValues[field] = null;
                }
            }else if(views != null && views["list"]){
                view = views["list"];
                for(let field of view.definition.structure){
                    fields.push(field.field);
                    selectedOperators[field] = null;
                    selectedValues[field] = null;
                }
            }
            call(view.model, "get_fields_desc", [fields]).then(
                (resp) => {
                    fieldsDescription = resp;
                }
            );
        }
    })

    function updateFilters(){
        filters = [];
        for(var field of fields){
            var operator = selectedOperators[field];
            var value = selectedValues[field];
            var value2 = selectedValues2[field];
            if(typeof(value) === "object"){
                if(value.id){
                    value = value.id;
                }
            }
            if(operator && (value || value2)){
                if(operator === "between"){
                    if(value){
                        filters.push([field,'>=',value]);
                    }
                    if(value2){
                        filters.push([field,'<=',value2]);
                    }
                }else{
                    filters.push([field, operator, value]);
                }
            }
        }
        filters = filters;
    }

    function openModal() {
        document.getElementById("button-modal").click();
    }

    function applyFilters(){
        publish({
            event: 'filtersChanged',
            filters: filters
        })
    }
</script>

<button id="button-modal" style="display:none" type="button" data-toggle="modal"
    data-target="#search-view-modal"></button>
<div id="search-view-modal" class="modal fade" tabindex="-1" role="dialog"
    aria-labelledby="searchView" aria-hidden="true">
    <div class="modal-dialog modal-lg">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">Filtros</h5>
                <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                <span aria-hidden="true">&times;</span>
                </button>
            </div>
            <div class="modal-body">
                <div class="form-group">
                    {#if fieldsDescription && view}
                        {#each view.definition.fields || view.definition.structure as item}
                            {#if item.field && item.field in fieldsDescription && !['manytomany','backref'].includes(fieldsDescription[item.field].type) }
                                <div class="search-row">
                                    <span style="width:30%">
                                        <label>{item.label || fieldsDescription[item.field].label}</label>
                                    </span>
                                    <span style="width:20%">
                                        <select class="form-control" bind:value={selectedOperators[item.field]}
                                            on:blur={updateFilters}>
                                            <option value="=">es</option>
                                            <option value="!=">no es</option>
                                            {#if ["integer","float","date","datetime"].includes(fieldsDescription[item.field].type)}
                                                <option value="&gt;">mayor que</option>
                                                <option value="&gt;=">mayor o igual que</option>
                                                <option value="&lt;">menor que</option>
                                                <option value="&lt;=">menor o igual que</option>
                                            {/if}
                                            {#if ["char","text","manytomany","backref"].includes(fieldsDescription[item.field].type)}
                                                <option value="ilike">contiene</option>
                                                <option value="not ilike">no contiene</option>
                                            {/if}
                                            {#if ["date"].includes(fieldsDescription[item.field].type)}
                                                <option value="between">entre</option>
                                            {/if}
                                        </select>
                                    </span>
                                    <span style="width:50%">
                                        <Field
                                            type={fieldsDescription[item.field].type}
                                            label={item.label || fieldsDescription[item.field].label}
                                            edit={true}
                                            bind:value={selectedValues[item.field]}
                                            model={fieldsDescription[item.field].model}
                                            choices={fieldsDescription[item.field].options}
                                            required={false}
                                            nolabel={true}
                                            on:change={updateFilters}
                                        />
                                        {#if selectedOperators[item.field] === "between"}
                                            <Field
                                                type={fieldsDescription[item.field].type}
                                                label={item.label || fieldsDescription[item.field].label}
                                                edit={true}
                                                bind:value={selectedValues2[item.field]}
                                                model={fieldsDescription[item.field].model}
                                                required={false}
                                                nolabel={true}
                                                on:change={updateFilters}
                                            />
                                        {/if}
                                    </span>
                                </div>
                            {/if}
                        {/each}
                    {/if}
                </div>
            </div>
            <div class="modal-footer">
                <button on:click={applyFilters} type="button" data-dismiss="modal"
                    class="btn btn-primary">Aplicar</button>
            </div>
        </div>
    </div>
</div>



<style>
    .search-row{
        display:flex;
        justify-content: space-evenly;
    }
    .search-row select{
        width:80px
    }
</style>