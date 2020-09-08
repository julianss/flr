<script>
    import CharField from './fields/CharField.svelte'
    import BooleanField from './fields/BooleanField.svelte'
    import TextField from './fields/TextField.svelte'
    import IntegerField from './fields/IntegerField.svelte'
    import FloatField from './fields/FloatField.svelte'
    import ForeignKeyField from './fields/ForeignKeyField.svelte'
    import DateField from './fields/DateField.svelte'
    import SelectField from './fields/SelectField.svelte'
    import ManyToManyField from './fields/ManyToManyField.svelte'
    import BackRefField from './fields/BackRefField.svelte'
    export let type;
    export let label;
    export let value;
    export let edit;
    export let password;
    export let model;
    export let filters = [];
    export let options = [];
    export let required;
    export let relatedFields;
    export let relatedFieldsDesc;
</script>

<div class={required?'field required':'field'}>
    {#if type}
        {#if type === "char"}
            <CharField
                label={label}
                bind:value={value}
                edit={edit}
                password={password}
            />
        {:else if type === "boolean"}
            <BooleanField
                label={label}
                bind:value={value}
                edit={edit}
            />
        {:else if type === "text"}
            <TextField
                label={label}
                bind:value={value}
                edit={edit}
            />
        {:else if type === "integer"}
            <IntegerField
                label={label}
                bind:value={value}
                edit={edit}
            />
        {:else if type === "float"}
            <FloatField
                label={label}
                bind:value={value}
                edit={edit}
            />
        {:else if type === "foreignkey" }
            <ForeignKeyField
                label={label}
                bind:value={value}
                edit={edit}
                model={model}
                filters={filters}
            />
        {:else if type === "date"}
            <DateField
                label={label}
                bind:value={value}
                edit={edit}
            />
        {:else if type === "select"}
            <SelectField
                label={label}
                bind:value={value}
                edit={edit}
                options={options}
            />
        {:else if type === "manytomany"}
            <ManyToManyField
                label={label}
                bind:value={value}
                edit={edit}
                model={model}
                filters={filters}
                relatedFields={relatedFields}
                relatedFieldsDesc={relatedFieldsDesc}
            />
        {:else if type === "backref"}
            <BackRefField
                label={label}
                bind:value={value}
                edit={edit}
                model={model}
                filters={filters}
                relatedFields={relatedFields}
                relatedFieldsDesc={relatedFieldsDesc}
            />
        {/if}
    {/if}
</div>

<style>
    .required :global(label::after){
        content:"*";
        color:red
    }
    .required :global(input, select){
        background-color:seashell
    }
</style>