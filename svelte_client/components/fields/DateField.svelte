<script>
    export let label = "";
    export let value;
    export let edit;
</script>

<div class="form-group">
    <label>{label}</label>
    {#if edit}
        <input class="form-control" type="date" bind:value={value}/>
    {:else}
        <p>{(value && new Date(value).toLocaleDateString()) || ''}</p>
    {/if}
</div>