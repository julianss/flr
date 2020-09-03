<script>
    export let label = "";
    export let value;
    export let edit;
    export let options = [];

    function getLabel(value){
        for(let o of options){
            if(o[0] === value){
                return o[1];
            }
        }
    }
</script>

<div class="form-group">
    <label>{label}</label>
    {#if edit}
        <select class="form-control" bind:value={value}>
            <option value={false}></option>
            {#each options as option}
                <option value={option[0]}>{option[1]}</option>
            {/each}
        </select>
    {:else}
        <p>{getLabel(value) || ''}</p>
    {/if}
</div>