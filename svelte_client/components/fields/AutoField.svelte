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
        <input class="form-control" bind:value={value} on:change={changed}/>
    {:else}
        <p>{value || ''}</p>
    {/if}
</div>