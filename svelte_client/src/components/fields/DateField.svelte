<script>
    import { createEventDispatcher } from 'svelte';
    import { renderDate } from './../../services/utils.js';
    const dispatch = createEventDispatcher();
    export let label = "";
    export let value;
    export let edit;
    export let readonly;
    export let options;

    function changed(){
        dispatch("change", {});
    }
</script>

<div class="form-group">
    <label>{label}</label>
    {#if edit & !readonly}
        <input class="form-control" type="date" bind:value={value} on:change={changed}/>
    {:else}
        <p>{renderDate(value)}</p>
    {/if}
</div>