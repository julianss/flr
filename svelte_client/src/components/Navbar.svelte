<script>
  import { _ } from 'svelte-i18n';
  import { getUserName, logout } from './../services/session.js'
  import { getMenus, getViews, openViews, clickMenu } from './../services/menu.js'
  import { onMount } from 'svelte';
  import { parseHash } from './../services/utils.js';

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

  function openPreferences(){
    getViews("FlrPreferences").then(
      (resp) => openViews(resp, {asWizard: true, showSaveButton: true, reloadOnSave: true})
    )
  }

  window.addEventListener('popstate', function(e){
    var params = parseHash();
    if(params.menu_id){
      clickMenu(parseInt(params.menu_id), params.type, params.id);
    }
  })

</script>

<nav class="navbar navbar-expand-lg navbar-dark bg-primary">
  <div class="container-fluid">
    <span class="navbar-brand">
      <img src="images/logo_navbar.png" alt="Logo"/>
    </span>
    <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-target="#navbarSupportedContent" aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
      <span class="navbar-toggler-icon"></span>
    </button>

    <div class="collapse navbar-collapse" id="navbarSupportedContent">
      <ul class="navbar-nav">
        {#each sections as section}
          {#if section.menus}
            <li class="nav-item dropdown">
              <a class="nav-link dropdown-toggle" href="#" id="navbarDropdown" role="button" data-bs-toggle="dropdown" aria-expanded="false">
                {section.name}
              </a>
              <div class="dropdown-menu" aria-labelledby="navbarDropdown">
                {#each section.menus as menu}
                  <li><a href="#" class="dropdown-item" type="button" on:click={()=>clickMenu(menu.id)}>{menu.name}</a></li>
                {/each}
              </div>
            </li>
          {/if}
        {/each}
      </ul>
      <ul class="navbar-nav ms-md-auto">
        <li class="nav-item dropdown">
            <a class="nav-link dropdown-toggle" href="#" id="navbarDropdownMenuLink" role="button"  data-bs-toggle="dropdown" aria-expanded="false"> 
              {username} 
            </a>
            <div class="dropdown-menu dropdown-menu-right" aria-labelledby="navbarDropdownMenuLink">
                <li><a href="#" class="dropdown-item" on:click={openPreferences}>{$_("navbar.preferences")}</a></li>
                <div class="dropdown-divider"></div>
                <li><a href="#" class="dropdown-item" on:click={logout}>{$_("navbar.logout")}</a></li>
            </div>
        </li>
      </ul>
    </div>
  </div>
</nav>