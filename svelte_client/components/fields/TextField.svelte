<script>
    import { createEventDispatcher } from 'svelte';
    const dispatch = createEventDispatcher();
    export let label = "";
    export let value;
    export let edit;
    export let readonly;

    function changed(){
        dispatch("change", {});
    }
</script>

<div class="form-group">
    <label>{label}</label>
    {#if edit && !readonly}
        <textarea class="form-control" bind:value={value} on:change={changed}/>
    {:else}
        <pre>{value || ''}</pre>
    {/if}
</div>