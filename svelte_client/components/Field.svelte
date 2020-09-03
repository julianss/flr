<script>
    import CharField from './fields/CharField.svelte'
    import BooleanField from './fields/BooleanField.svelte'
    import TextField from './fields/TextField.svelte'
    export let type;
    export let label;
    export let value;
    export let edit;
    export let password;
</script>

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
    {/if}
{/if}