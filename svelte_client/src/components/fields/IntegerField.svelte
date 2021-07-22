<script>
    import { _ } from 'svelte-i18n';
    import { createEventDispatcher } from 'svelte';
    const dispatch = createEventDispatcher();
    export let label = "";
    export let value;
    export let edit;
    export let readonly;
    export let options;

    function changed(){
        if (options && options.hasOwnProperty('minVal') && value < options.minVal){
            options.minValError = true;
        }else if (options && options.hasOwnProperty('maxVal') && value > options.maxVal){
            options.maxValError = true;
        }else{
            dispatch("change", {});
        }
    }
    function resetValidations(){
        if (options && options.minValError){
            options.minValError = false
        }
        if (options && options.maxValError){
            options.maxValError = false
        }
    }
</script>

<div class="form-group">
    <label>{label}</label>
    {#if edit && !readonly}
        <input class="form-control" type="number" bind:value={value} on:change={changed}/>
        {#if options && (options.minValError || options.maxValError)}
            <div class="alert alert-dismissible alert-danger" role="alert">
                <button type="button" class="close" data-dismiss="alert"
                    on:click={resetValidations}>×</button>
                {#if options.minValError}
                    <strong>{$_('form_view.min_value')} {options.minVal}</strong><br>
                {:else if options.maxValError}
                    <strong>{$_('form_view.max_value')} {options.maxVal}</strong><br>
                {/if}
            </div>
        {/if}
    {:else}
        <p>{value}</p>
    {/if}
</div>