<script>
    export let label = "";
    export let value;
    export let edit;
    export let password = false;
</script>

<div class="form-group">
    <label>{label}</label>
    {#if edit && password}
        <input class="form-control" type="password" bind:value={value}/>
    {:else if edit && !password}
        <input class="form-control" type="text" bind:value={value}/>
    {:else if password}
        <p>*****</p>
    {:else}
        <p>{value}</p>
    {/if}
</div>