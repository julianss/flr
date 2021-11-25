<script>
    import { call } from "../../services/service.js";
    import Field from "../Field.svelte";
    import ForeignKeyField from './ForeignKeyField.svelte';
    import { createEventDispatcher } from 'svelte';
    const dispatch = createEventDispatcher();
    export let label = "";
    export let model = "";
    export let model_name_field;
    export let filters = [];
    export let value = [];
    export let edit;
    export let relatedFieldsDesc = {};
    export let viewtype;
    export let readonly;
    export let options;

    function renderField(obj, field){
        let val = obj[field];
        if (typeof(val)=="undefined"){
            return "";
        }else if(typeof(val) == "number" || typeof(val) == "string"){
            return val;
        }else if(typeof(val) == "boolean"){
            return val?"✔️":"❌";
        }else if(typeof(val) === "object"){
            return val.name || val.id;
        }else{
            return val;
        }

    }

    function remove(id){
        for(let i=0;i<value.length;i++){
            if(value[i].id==id){
                value.splice(i,1);
                value = value;
                break;
            }
        }
        changed();
    }

    function newElement(){
        let tmpId = "tmp_" + Date.now().toString() + "-" + Math.random().toString().substring(2);
        let blankRecord = {id: tmpId};
        for(let field of options.related_fields){
            blankRecord[field.field] = null;
        }
        if(!value){
            value = [];
        }
        value.push(blankRecord);
        value = value;
        changed();
    }

    function changed(){
        dispatch("change", {});
    }

    function selectResult(result){
        dispatch("change", result);
    }
</script>

<div class="form-group">
    <label>{label}</label>
    {#if viewtype === 'form'}
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
                            <td>
                                <Field
                                    type={relatedFieldsDesc[field.field].type}
                                    label={relatedFieldsDesc[field.field].label}
                                    edit={edit && !field.readonly}
                                    bind:value={obj[field.field]}
                                    model={relatedFieldsDesc[field.field].model}
                                    model_name_field={relatedFieldsDesc[field.field].model_name_field}
                                    choices={relatedFieldsDesc[field.field].options}
                                    required={relatedFieldsDesc[field.field].required}
                                    relatedFieldsDesc={null}
                                    on:change={changed}
                                    nolabel={true}
                                    readonly={field.readonly}
                                    options={field.options || {}}
                                    filters={[]}
                                    viewtype={viewtype}
                                />
                            </td>
                        {/each}
                        <td class="basura">
                            {#if options && options.remove}
                                <button
                                    class="btn btn-info"
                                    hidden={!edit}
                                    on:click={()=>remove(obj.id)}>
                                    <img
                                        src="icons/trash-fill.svg"
                                        style="filter:invert(1)"
                                        alt="Eliminar"/>
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
        {#if edit && options.add}
            <button type="button" class="btn btn-secondary new-element" on:click={newElement}>
                + Agregar elemento
            </button>
        {/if}
    {:else if viewtype==='list'}
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
            on:change={selectResult}
            query={
                value&&options&&options.name_field?value[options.name_field]:
                value&&options&&options.related_fields?
                    options.related_fields.map(item => value[item.field]).join(' - '):
                value?value[model_name_field]:''}
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
    .new-element{
        margin: 5px 5px 5px 5px
    }
</style>
