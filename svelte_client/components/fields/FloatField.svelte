<script>
    export let label = "";
    export let value;
    export let edit;
</script>

<div class="form-group">
    <label>{label}</label>
    {#if edit}
        <input class="form-control" type="number" bind:value={value}/>
    {:else}
        <p>{value || ''}</p>
    {/if}
</div>