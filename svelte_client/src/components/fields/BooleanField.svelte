<script>
    import { createEventDispatcher } from 'svelte';
    const dispatch = createEventDispatcher();
    export let label = "";
    export let value;
    export let edit;
    export let readonly;
    export let viewtype;

    function changed(){
        dispatch("change", "");
    }
</script>

<div class="form-group">
    <label>{label}</label>
    {#if viewtype==='search'}
        <select class="form-control" bind:value={value} on:click={changed} on:keyup={changed}>
            <option value={null}></option>
            <option value={true}>True</option>
            <option value={false}>False</option>
        </select>
    {:else}
        {#if edit && !readonly}
        <div>
            <input type="checkbox" bind:checked={value} on:change={changed}/>
        </div>
        {:else}
            <div>
                {#if value}
                    <span class="true">✔️</span>
                {:else}
                    <span class="false">❌</span>
                {/if}
            </div>
        {/if}
    {/if}
</div>

<style>
    input{
       width:20px;
       height:20px;
    }
    .true{
        color:green;
        font-weight:bold;
        font-size:larger;
    }
    .false{
        color:red;
        font-weight:bold;
        font-size:larger;
    }
</style>