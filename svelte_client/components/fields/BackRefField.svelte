<script>
    import { call } from "../../services/service.js";
    import Field from "../Field.svelte";
    import { createEventDispatcher } from 'svelte';
    const dispatch = createEventDispatcher();
    export let label = "";
    export let model = "";
    export let filters = [];
    export let value = [];
    export let edit;
    export let relatedFields = [];
    export let relatedFieldsDesc = {};
    export let allowAdd;
    export let allowRemove;
    let valueFK;

    function renderField(obj, field){
        let val = obj[field];
        if(typeof(val) == "number" || typeof(val) == "string"){
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
        for(let field of relatedFields){
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
</script>

<div class="form-group">
    <label>{label}</label>
    {#if edit && allowAdd}
        <button type="button" class="btn btn-secondary new-element" on:click={newElement}>
            + Agregar elemento
        </button>
    {/if}
    <table class="table table-sm">
        <thead class="thead-light">
            <tr>
                {#each relatedFields as field}
                    {#if !relatedFieldsDesc || !relatedFieldsDesc[field.field]}
                        <th>{field.field}</th>
                    {:else}
                        <th>{relatedFieldsDesc[field.field].label}</th>
                    {/if}
                {/each}
                <th></th>
            </tr>
        </thead>
        {#if (value || []).length>0}
            {#each value as obj}
                <tr>
                    {#each relatedFields as field}
                        {#if !edit || field.readonly}
                            <td>{renderField(obj, field.field)}</td>
                        {:else}
                            <td>
                                <Field
                                    type={relatedFieldsDesc[field.field].type}
                                    label={relatedFieldsDesc[field.field].label}
                                    edit={true}
                                    bind:value={obj[field.field]}
                                    password={false}
                                    model={relatedFieldsDesc[field.field].model}
                                    options={relatedFieldsDesc[field.field].options}
                                    required={relatedFieldsDesc[field.field].required}
                                    relatedFields={null}
                                    relatedFieldsDesc={null}
                                    nolabel={true}
                                    on:change={changed}
                                    add={null}
                                    remove={null}
                                />
                            </td>
                        {/if}
                    {/each}
                    <td class="basura">
                        {#if allowRemove}
                            <img
                                hidden={!edit}
                                on:click={()=>remove(obj.id)}
                                src="icons/trash-fill.svg"
                                alt="Eliminar"/>
                        {/if}
                    </td>
                </tr>
            {/each}
        {:else}
            <tr>
                <td colspan="100">(Sin elementos)</td>
            </tr>
        {/if}
    </table>
</div>

<style>
    table{
        border: 1px solid silver;
        background-color: white;
    }
    .basura{
        text-align:right;
        cursor: pointer;
    }
    .new-element{
        margin: 5px 5px 5px 5px
    }
</style>