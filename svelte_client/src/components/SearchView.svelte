<script>
    import { _ } from 'svelte-i18n';
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
                    selectedValues[field.field] = null;
                    selectedValues2[field.field] = null;
                }
            }else if(views != null && views["list"]){
                view = views["list"];
                for(let field of view.definition.structure){
                    fields.push(field.field);
                    selectedValues[field.field] = null;
                    selectedValues2[field.field] = null;
                }
            }else{
                view = null;
            }
            //There may be no list nor search view (eg. wizard)
            if(!view){
                return;
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
            var type = field in fieldsDescription?fieldsDescription[field].type:null;
            if(value && typeof(value) === "object"){
                if(value.id){
                    value = value.id;
                }
            }
            if(type && ["date", "datetime"].includes(type)){
                if(value == ''){
                    value = null;
                }
                if(value2 == ''){
                    value2 = null;
                }
            }
            if(operator && (value!==null || value2!==null)){
                if(operator === "between"){
                    if(value){
                        filters.push([field,'>=',value]);
                    }
                    if(value2){
                        filters.push([field,'<=',value2]);
                    }
                }else if (value === false){
                    if (type && type==='boolean'){
                        filters.push([field, operator, false]);
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

<button id="button-modal" style="display:none" type="button" data-bs-toggle="modal"
    data-bs-target="#search-view-modal"></button>
<div id="search-view-modal" class="modal fade" tabindex="-1" role="dialog"
    aria-labelledby="searchView" aria-hidden="true">
    <div class="modal-dialog modal-lg">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">{$_("search_view.filters")}</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"/>
            </div>
            <div class="modal-body">
                <div class="form-group">
                    {#if fieldsDescription && view}
                        {#each view.definition.fields || view.definition.structure as item}
                            {#if item.field && item.field in fieldsDescription}
                                <div class="search-row">
                                    <span style="width:30%">
                                        <label>{item.label || fieldsDescription[item.field].label}</label>
                                    </span>
                                    <span style="width:20%">
                                        <select class="form-control" bind:value={selectedOperators[item.field]}
                                            on:blur={updateFilters}>
                                            <option value=""></option>
                                            {#if ["manytomany","backref"].includes(fieldsDescription[item.field].type)}
                                                <option value="in">{$_("search_view.is")}</option>
                                                <option value="not in">{$_("search_view.is_not")}</option>
                                            {:else}
                                                <option value="=">{$_("search_view.is")}</option>
                                                <option value="!=">{$_("search_view.is_not")}</option>
                                            {/if}
                                            {#if ["integer","float","date","datetime"].includes(fieldsDescription[item.field].type)}
                                                <option value="&gt;">{$_("search_view.gt")}</option>
                                                <option value="&gt;=">{$_("search_view.gte")}</option>
                                                <option value="&lt;">{$_("search_view.lt")}</option>
                                                <option value="&lt;=">{$_("search_view.lte")}</option>
                                            {/if}
                                            {#if ["char","text"].includes(fieldsDescription[item.field].type)}
                                                <option value="ilike">{$_("search_view.contains")}</option>
                                                <option value="not ilike">{$_("search_view.doesnt_contain")}</option>
                                            {/if}
                                            {#if ["date"].includes(fieldsDescription[item.field].type)}
                                                <option value="between">{$_("search_view.between")}</option>
                                            {/if}
                                        </select>
                                    </span>
                                    <span style="width:50%">
                                        <div hidden={selectedOperators[item.field]==''}>
                                            <Field
                                                type={fieldsDescription[item.field].type}
                                                label={item.label || fieldsDescription[item.field].label}
                                                edit={true}
                                                bind:value={selectedValues[item.field]}
                                                model={fieldsDescription[item.field].model}
                                                model_name_field={fieldsDescription[item.field].model_name_field}
                                                choices={fieldsDescription[item.field].options}
                                                required={false}
                                                relatedFieldsDesc={fieldsDescription[item.field].related_fields}
                                                on:change={updateFilters}
                                                nolabel={true}
                                                readonly={false}
                                                filters={[]}
                                                viewtype={'search'}
                                                options={item.options || {}}
                                            />
                                            {#if selectedOperators[item.field] === "between"}
                                                <Field
                                                    type={fieldsDescription[item.field].type}
                                                    label={item.label || fieldsDescription[item.field].label}
                                                    edit={true}
                                                    bind:value={selectedValues2[item.field]}
                                                    model={fieldsDescription[item.field].model}
                                                    model_name_field={fieldsDescription[item.field].model_name_field}
                                                    choices={fieldsDescription[item.field].options}
                                                    required={false}
                                                    relatedFieldsDesc={fieldsDescription[item.field].related_fields}
                                                    on:change={updateFilters}
                                                    nolabel={true}
                                                    readonly={false}
                                                    filters={[]}
                                                    viewtype={'search'}
                                                    options={item.options || {}}
                                                />
                                            {/if}
                                        </div>
                                    </span>
                                </div>
                            {/if}
                        {/each}
                    {/if}
                </div>
            </div>
            <div class="modal-footer">
                <button on:click={applyFilters} type="button" data-bs-dismiss="modal"
                    class="btn btn-primary">{$_("search_view.apply")}</button>
            </div>
        </div>
    </div>
</div>



<style>
    .search-row{
        display:flex;
        justify-content: space-evenly;
        margin-bottom:3px;
    }
    .search-row select{
        width:80px
    }
</style>