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
  })

  function clickMenu(menuId) {
    getViews(menuId).then(
      (resp) => {
        let loadedViews = {};
        let firstType = null;
        for(let view of resp){
          loadedViews[view.view_type] = view;
          if(firstType === null){
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
    )
  }
</script>

<nav class="navbar navbar-expand-lg navbar-dark bg-primary">
  <a class="navbar-brand" href="#">My App</a>
  <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarSupportedContent" aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
    <span class="navbar-toggler-icon"></span>
  </button>

  <div class="collapse navbar-collapse" id="navbarSupportedContent">
    <ul class="navbar-nav w-100">
      {#each sections as section}
        {#if section.menus}
          <li class="nav-item dropdown">
            <a class="nav-link dropdown-toggle" href="#" id="navbarDropdown" role="button" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
              {section.name}
            </a>
            <div class="dropdown-menu" aria-labelledby="navbarDropdown">
              {#each section.menus as menu}
                <a class="dropdown-item" href="#" on:click={()=>clickMenu(menu.id)}>{menu.name}</a>
              {/each}
            </div>
          </li>
        {/if}
      {/each}
      <li class="nav-item dropdown ml-auto">
          <a class="nav-link dropdown-toggle" href="#" id="navbarDropdownMenuLink" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false"> {username} </a>
          <div class="dropdown-menu dropdown-menu-right" aria-labelledby="navbarDropdownMenuLink">
              <a class="dropdown-item" href="#" on:click={logout}>Cerrar sesión</a>
          </div>
      </li>
    </ul>

  </div>
</nav>
