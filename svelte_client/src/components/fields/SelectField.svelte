<script>
    import { createEventDispatcher } from 'svelte';
    const dispatch = createEventDispatcher();
    export let label = "";
    export let value;
    export let edit;
    export let choices = [];
    export let readonly;

    function getLabel(value){
        for(let o of choices){
            if(o[0] === value){
                return o[1];
            }
        }
    }

    function changed(){
        dispatch("change", {});
    }

</script>

<div class="form-group">
    <label>{label}</label>
    {#if edit && !readonly}
        <select class="form-control" bind:value={value} on:click={changed} on:keyup={changed}>
            <option value={false}></option>
            {#each choices as option}
                <option value={option[0]}>{option[1]}</option>
            {/each}
        </select>
    {:else}
        <p>{getLabel(value) || ''}</p>
    {/if}
</div>