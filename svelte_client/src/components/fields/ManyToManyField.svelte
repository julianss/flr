<script>
    import ForeignKeyField from './ForeignKeyField.svelte';
    import { createEventDispatcher } from 'svelte';
    import { call } from "../../services/service.js"
    const dispatch = createEventDispatcher();
    export let label = "";
    export let model = "";
    export let model_name_field="";
    export let filters = [];
    export let value = [];
    export let edit;
    export let relatedFieldsDesc = {};
    export let readonly;
    export let viewtype;
    export let options;
    let valueFK = null;

    function renderField(obj, field){
        let val = obj[field];
        if(typeof(val) == "number" || typeof(val) == "string"){
            return val;
        }else if(typeof(val) === "object"){
            return val.name || val.id;
        }else{
            return val;
        }

    }

    function add(event){
        if(!event.detail.id){
            return;
        }
        let ids = [];

        if (!value){
            value = [];
        }
        for(let obj of value){
            ids.push(obj.id);
        }
        if(!ids.includes(event.detail.id)){
            value.push(event.detail);
            value = value;
        }
    }

    function changed(result){
        dispatch('change', result);
    }

    function remove(id){
        for(let i=0;i<value.length;i++){
            if(value[i].id==id){
                value.splice(i,1);
                value = value;
                break;
            }
        }
    }
</script>

<div class="form-group">
    <label>{label}</label>
    {#if viewtype === 'form'}
        {#if edit && (options||{}).add!==false && !readonly}
            <ForeignKeyField
                label=""
                bind:value={valueFK}
                edit={edit}
                model={model}
                model_name_field={model_name_field}
                filters={filters}
                on:change={add}
                readonly={false}
                placeholder="Agregar elemento"
                options={options}
            />
        {/if}
        <table class="table table-sm">
            <thead class="thead-light">
                <tr>
                    {#each options.related_fields || [] as field}
                        {#if !relatedFieldsDesc || !relatedFieldsDesc[field.field]}
                            <th>{field.field}</th>
                        {:else}
                            <th>{relatedFieldsDesc[field.field].label}</th>
                        {/if}
                    {/each}
                    <th></th>
                </tr>
            </thead>
            <tbody>
            {#if (value || []).length>0}
                {#each value as obj}
                    <tr>
                        {#each options.related_fields || [] as field}
                            <td>{renderField(obj, field.field)}</td>
                        {/each}
                        <td class="basura">
                            {#if options && options.remove}
                                <button class="btn btn-info mb-2"
                                    hidden={!edit}
                                    on:click={()=>remove(obj.id)}
                                >
                                    <img
                                        style="filter:invert(1)"
                                        src="icons/trash-fill.svg"
                                        alt="Remover"/>
                                </button>
                            {/if}
                        </td>
                    </tr>
                {/each}
            {:else}
                <tr>
                    <td colspan="100">(Sin elementos)</td>
                </tr>
            {/if}
            </tbody>
        </table>
    {:else if viewtype === 'list'}
        {#if (value || []).length>0}
            {#each value as obj}
                {#each options.related_fields || [] as field}
                    <p>{renderField(obj, field.field)}</p>
                {/each}
            {/each}
        {/if}
    {:else if viewtype === 'search'}
        <ForeignKeyField
            label=""
            bind:value={value}
            edit={edit}
            model={model}
            model_name_field={model_name_field}
            filters={filters}
            on:change={changed}
            query={
                value&&options&&options.name_field?
                value[options.name_field]:value?value[model_name_field]:''}
            readonly={false}
            placeholder=""
            options={options}
        />
    {/if}
</div>

<style>
    .basura{
        text-align:right;
        cursor: pointer;
    }
</style>
