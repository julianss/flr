<script>
  import { getUserName, logout } from './../services/session.js'
  import { getMenus, getViews, openViews } from './../services/menu.js'
  import { onMount } from 'svelte';
  import { parseHash, updateHash, replaceHash } from './../services/utils.js';
  import { publish } from './../services/writables.js';

  let sections = [];
  let username = "";

  onMount(async () => {
    sections = await getMenus();
    username = await getUserName();
    var params = parseHash();
    if(params.menu_id){
      clickMenu(parseInt(params.menu_id), params.type, params.id);
    }else{
      clickMenu(sections[0].menus[0].id);
    }
  })

  function clickMenu(menuId, type, id) {
    if(menuId){
      getViews(menuId).then(
        (resp) => {
          openViews(resp);
          if(type == 'form' && id){
            updateHash({
              menu_id: menuId,
              type: 'form',
              id: id
            })
            publish({
              event: 'activeViewChanged',
              type: 'form'
            })
            publish({
              event: 'activeRecordIdChanged',
              id: parseInt(id)
            })
          }else{
            replaceHash({menu_id: menuId})
          }
        }
      )
    }
  }

  function loadView(view){
    getViews(view).then((resp) => openViews(resp))
  }

  window.addEventListener('popstate', function(e){
    var params = parseHash();
    if(params.menu_id){
      clickMenu(parseInt(params.menu_id), params.type, params.id);
    }
  })

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
                <button class="dropdown-item" type="button" on:click={()=>clickMenu(menu.id)}>{menu.name}</button>
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