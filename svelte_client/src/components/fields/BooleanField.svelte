<script>
    import { createEventDispatcher } from 'svelte';
    const dispatch = createEventDispatcher();
    export let label = "";
    export let value;
    export let edit;
    export let readonly;

    function changed(){
        dispatch("change", "");
    }
</script>

<div class="form-group">
    <label>{label}</label>
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