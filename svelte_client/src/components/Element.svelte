<script>
    export let tag;
    export let text;
</script>

{#if tag == "h1"}
    <h1>{text}</h1>
{:else if tag=="h2"}
    <h2>{text}</h2>
{:else if tag=="h3"}
    <h3>{text}</h3>
{:else if tag=="h4"}
    <h4>{text}</h4>
{:else if tag=="h5"}
    <h5>{text}</h5>
{:else if tag=="h6"}
    <h6>{text}</h6>
{:else if tag=="p"}
    <p>{text}</p>
{/if}
