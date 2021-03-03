<script>
    import { createEventDispatcher } from 'svelte';
    import { renderDateTime } from './../../services/utils.js';
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
    {#if edit & !readonly}
        <input class="form-control" type="datetime-local" bind:value={value} on:change={changed}/>
    {:else}
        <p>{renderDateTime(value)}</p>
    {/if}
</div>