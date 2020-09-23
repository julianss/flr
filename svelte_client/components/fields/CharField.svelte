<script>
    import { createEventDispatcher } from 'svelte';
    const dispatch = createEventDispatcher();
    export let label = "";
    export let value;
    export let edit;
    export let password = false;
    export let readonly;

    function changed(){
        dispatch("change", {});
    }
</script>

<div class="form-group">
    <label>{label}</label>
    {#if edit && password && !readonly}
        <input class="form-control" type="password" bind:value={value} on:change={changed}/>
    {:else if edit && !password && !readonly}
        <input class="form-control" type="text" bind:value={value} on:change={changed}/>
    {:else if password}
        <p>*****</p>
    {:else}
        <p>{value || ''}</p>
    {/if}
</div>