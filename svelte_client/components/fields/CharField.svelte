<script>
    import { createEventDispatcher } from 'svelte';
    const dispatch = createEventDispatcher();
    export let label = "";
    export let value;
    export let edit;
    export let password = false;
    export let viewpassword;
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
    <div class="input-group">
        {#if edit && password && !readonly}
            <input
                class="form-control"
                type="password" bind:value={value} on:change={changed} id="input-{uniqueId}"/>
            {#if viewpassword}
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
        {:else if edit && !password && !readonly}
            <input class="form-control" type="text" bind:value={value} on:change={changed}/>
        {:else if password}
            <p>*****</p>
        {:else if options && options.html}
            {@html (value || '')}
        {:else}
            <p>{value || ''}</p>
        {/if}
    </div>
</div>