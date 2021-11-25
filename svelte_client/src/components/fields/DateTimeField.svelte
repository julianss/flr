<script>
    import { onMount } from 'svelte';
    import { createEventDispatcher } from 'svelte';
    import { UTCtoLocal, localToUTC, renderDateTime } from './../../services/utils.js';
    const dispatch = createEventDispatcher();
    export let label = "";
    export let value;
    export let edit;
    export let readonly;
    export let options;
    let valueLocal;

    function changed(){
        value = localToUTC(valueLocal);
        dispatch("change", {});
    }

    onMount(async () => {
		valueLocal = UTCtoLocal(value);
	});

</script>

<div class="form-group">
    <label>{label}</label>
    {#if edit & !readonly}
        <input class="form-control" type="datetime-local" bind:value={valueLocal} on:change={changed} step="1"/>
    {:else}
        <p>{value && renderDateTime(value)}</p>
    {/if}
</div>