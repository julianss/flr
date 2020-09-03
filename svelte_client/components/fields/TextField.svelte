<script>
    export let label = "";
    export let value;
    export let edit;
</script>

<div class="form-group">
    <label>{label}</label>
    {#if edit}
        <textarea class="form-control" bind:value={value}/>
    {:else}
        <pre>{value || ''}</pre>
    {/if}
</div>