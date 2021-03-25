<script>
    import { createEventDispatcher } from 'svelte';
    const dispatch = createEventDispatcher();
    export let label = "";
    export let value;
    export let edit;
    export let readonly;
    export let options;
    let uniqueId = Date.now().toString() + "-" + Math.random().toString().substring(2);

    function changed(){
        dispatch("change", {});
    }

    function viewPassword(){
        var inputObj = document.getElementById(`input-${uniqueId}`);
        if (inputObj){
            var buttonImg = document.getElementById(`input-${uniqueId}-img`)
            if (inputObj.type === "password"){
                inputObj.type = "text";
                buttonImg.src = "icons/eye-slash.svg"
            }else{
                inputObj.type = "password";
                buttonImg.src = "icons/eye.svg"
            }
            inputObj.focus()
        }
    }

</script>

<div class="form-group">
    <label>{label}</label>
    {#if edit && options && options.password && !readonly}
        <div class="input-group">
            <input
                class="form-control"
                type="password" bind:value={value} on:change={changed} id="input-{uniqueId}"/>
            {#if options && options.viewpassword}
                <div class="input-group-prepend border-right-0">
                    <button
                        tabindex="-1"
                        type="button"
                        class="btn border border-left-0 pb-1"
                        on:click={() => viewPassword()}>
                        <img id="input-{uniqueId}-img" src="icons/eye.svg" alt=""/>
                    </button>
                </div>
            {/if}
        </div>
    {:else if edit && !(options && options.password) && !readonly}
        <input class="form-control" type="text" bind:value={value} on:change={changed}/>
    {:else if options && options.password}
        <p>*****</p>
    {:else if options && options.html}
        {@html (value || '')}
    {:else if options && options.url}
        {#if options.url === true}
            <a target="blank" href={value}>{value}</a>
        {:else}
            <a target="blank" href={value}>{options.url}</a>
        {/if}
    {:else}
        <p>{value || ''}</p>
    {/if}
</div>