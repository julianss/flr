<script>
  import { getUserName, logout } from './../services/session.js'
  import { getMenus, getViews } from './../services/menu.js'
  import { onMount } from 'svelte';
  import { publish } from './../services/writables.js';

  let sections = [];
  let username = "";

  onMount(async () => {
    sections = await getMenus();
    username = await getUserName();
    clickMenu(sections[0].menus[0]);
  })

  function clickMenu(menu) {
    getViews(menu.id).then((resp) => openViews(resp))
  }

  function loadView(view){
    getViews(view).then((resp) => openViews(resp))
  }

  function openViews(resp){
    let loadedViews = {};
    let firstType = null;
    for(let view of resp){
      loadedViews[view.view_type] = view;
      if (view.menu_id){
        loadedViews[view.view_type]['menu_view_name'] = view.menu_id.name;
      }
      else {
        loadedViews[view.view_type]['menu_view_name'] = view.name;
      }
      if(firstType === null && view.view_type != "search"){
        firstType = view.view_type;
      }
    }
    publish({
      event: 'viewsChanged',
      views: loadedViews,
    });
    publish({
      event: 'activeRecordIdChanged',
      id: null,
    })
    publish({
      event: 'activeViewChanged',
      type: firstType,
    })
  }

</script>

<nav class="navbar navbar-expand-lg navbar-dark bg-primary">
  <span class="navbar-brand">
    <img src="" style="width:200px" alt="Logo"/>
  </span>
  <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarSupportedContent" aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
    <span class="navbar-toggler-icon"></span>
  </button>

  <div class="collapse navbar-collapse" id="navbarSupportedContent">
    <ul class="navbar-nav w-100">
      {#each sections as section}
        {#if section.menus}
          <li class="nav-item dropdown">
            <button class="btn btn-secondary remove-button-css dropdown-toggle" id="navbarDropdown" type="button" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
              {section.name}
            </button>
            <div class="dropdown-menu" aria-labelledby="navbarDropdown">
              {#each section.menus as menu}
                <button class="dropdown-item" type="button" on:click={()=>clickMenu(menu)}>{menu.name}</button>
              {/each}
            </div>
          </li>
        {/if}
      {/each}
      <li class="nav-item dropdown ml-auto">
          <button class="btn btn-secondary remove-button-css dropdown-toggle" id="navbarDropdownMenuLink" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false"> {username} </button>
          <div class="dropdown-menu dropdown-menu-right" aria-labelledby="navbarDropdownMenuLink">
              <a class="dropdown-item" href="#" on:click={()=>loadView('FlrPreferences')}>Preferencias</a>
              <div class="dropdown-divider"></div>
              <a class="dropdown-item" href="#" on:click={logout}>Cerrar sesión</a>
          </div>
      </li>
    </ul>

  </div>
</nav>

<style>
  .remove-button-css {
    outline: none;
    border: 0px;
    box-sizing: none;
    background-color: transparent;
  }
</style>