<script>
    import CharField from './fields/CharField.svelte'
    import BooleanField from './fields/BooleanField.svelte'
    import TextField from './fields/TextField.svelte'
    import IntegerField from './fields/IntegerField.svelte'
    import FloatField from './fields/FloatField.svelte'
    import ForeignKeyField from './fields/ForeignKeyField.svelte'
    import DateField from './fields/DateField.svelte'
    import DateTimeField from './fields/DateTimeField.svelte'
    import SelectField from './fields/SelectField.svelte'
    import ManyToManyField from './fields/ManyToManyField.svelte'
    import BackRefField from './fields/BackRefField.svelte'
    import FileField from './fields/FileField.svelte'
    import AutoField from './fields/AutoField.svelte'
    import { createEventDispatcher } from 'svelte';
    const dispatch = createEventDispatcher();
    export let type;
    export let label;
    export let value;
    export let edit;
    export let model;
    export let model_name_field;
    export let filters;
    export let choices = [];
    export let required;
    export let relatedFieldsDesc;
    export let nolabel;
    export let readonly;
    export let viewtype;
    export let options;
    function changed(){
        dispatch("change", {});
    }

    function getClass(){
        let classes = ["field"];
        if(required){
            classes.push("required");
        }
        if(nolabel){
            classes.push("nolabel");
        }
        if (viewtype === 'list'){
            classes.push("nomargin");
        }
        return classes.join(" ");
    }
</script>

<div class={(required || nolabel || true) && getClass()}>
    {#if type}
        {#if type === "char"}
            <CharField
                label={label}
                bind:value={value}
                edit={edit}
                on:change={changed}
                readonly={readonly}
                options={options}
            />
        {:else if type === "boolean"}
            <BooleanField
                label={label}
                bind:value={value}
                edit={edit}
                on:change={changed}
                readonly={readonly}
                viewtype={viewtype}
            />
        {:else if type === "text"}
            <TextField
                label={label}
                bind:value={value}
                edit={edit}
                on:change={changed}
                readonly={readonly}
                options={options}
            />
        {:else if type === "integer"}
            <IntegerField
                label={label}
                bind:value={value}
                edit={edit}
                on:change={changed}
                readonly={readonly}
                options={options}
            />
        {:else if type === "float"}
            <FloatField
                label={label}
                bind:value={value}
                edit={edit}
                on:change={changed}
                readonly={readonly}
                options={options}
            />
        {:else if type === "foreignkey" }
            <ForeignKeyField
                label={label}
                bind:value={value}
                edit={edit}
                model={model}
                model_name_field={model_name_field}
                filters={filters}
                on:change={changed}
                query={
                    value&&options&&options.name_field?
                    value[options.name_field]:value?value[model_name_field]:''}
                readonly={readonly}
                options={options}
            />
        {:else if type === "date"}
            <DateField
                label={label}
                bind:value={value}
                edit={edit}
                on:change={changed}
                readonly={readonly}
            />
        {:else if type === "datetime"}
            <DateTimeField
                label={label}
                bind:value={value}
                edit={edit}
                on:change={changed}
                readonly={readonly}
            />
        {:else if type === "select"}
            <SelectField
                label={label}
                bind:value={value}
                edit={edit}
                choices={choices}
                on:change={changed}
                readonly={readonly}
            />
        {:else if type === "manytomany"}
            <ManyToManyField
                label={label}
                bind:value={value}
                edit={edit}
                model={model}
                model_name_field={model_name_field}
                filters={filters}
                relatedFieldsDesc={relatedFieldsDesc}
                on:change={changed}
                readonly={readonly}
                options={options}
                viewtype={viewtype}
            />
        {:else if type === "backref"}
            <BackRefField
                label={label}
                bind:value={value}
                edit={edit}
                model={model}
                model_name_field={model_name_field}
                filters={filters}
                relatedFieldsDesc={relatedFieldsDesc}
                on:change={changed}
                readonly={readonly}
                options={options}
                viewtype={viewtype}
            />
        {:else if type === "file"}
            <FileField
                label={label}
                bind:value={value}
                edit={edit}
                on:change={changed}
                readonly={readonly}
                options={options}
                viewtype={viewtype}
            />
        {:else if type === "auto"}
            <AutoField
                label={label}
                bind:value={value}
                edit={edit}
                readonly={readonly}
                on:change={changed}
            />
        {/if}
    {/if}
</div>

<style>
    .required :global(label:not(:empty)::after){
        content:"*";
        color:red
    }
    /* .required :global(input){
        background-color:seashell
    }
    .required :global(select){
        background-color:seashell
    } */
    .nolabel :global(label){
        display: none
    }
    .nomargin :global(.form-group, .form-group .input-group p) {
        margin-bottom: 0px
    }
    :global(.form-group label){
        font-weight: bold;
    }

</style>