<template>
  <div class="wrap">
    <header class="global">
        <div class="date-search">
        </div>
        <div class="branding">
          <h1><a><img class="logo" src="../assets/images/logo1.png" alt="Pa Logo" /></a></h1>
        </div>
        <nav>
            <div id="hamburger"><i class="icon-menu"></i> Menu</div>
            <ul class="sf-menu">
            <li class="home">
            <a href="#" title="Home"><i class="icon-home"></i><span> Home</span></a>
            </li>
                <li>
                <a href="#">Meu Perfil</a>
                </li>
            </ul>
        </nav>
    </header>
  </div>
</template>

<script>

</script>


<style scoped>
@import url("https://fonts.googleapis.com/css?family=Droid+Sans:400,700");

@font-face {
  font-family: 'mindshare';
  src: url("https://s3-us-west-2.amazonaws.com/s.cdpn.io/72900/mindshare.eot?95499031");
  src: url("https://s3-us-west-2.amazonaws.com/s.cdpn.io/72900/mindshare.eot?95499031#iefix") format("embedded-opentype"), url("https://s3-us-west-2.amazonaws.com/s.cdpn.io/72900/mindshare.woff?95499031") format("woff"), url("https://s3-us-west-2.amazonaws.com/s.cdpn.io/72900/mindshare.ttf?95499031") format("truetype"), url("https://s3-us-west-2.amazonaws.com/s.cdpn.io/72900/mindshare.svg?95499031#mindshare") format("svg");
  font-weight: normal;
  font-style: normal; }

[class^="icon-"]:before, [class*=" icon-"]:before {
  font-family: "mindshare";
  font-style: normal;
  font-weight: normal;
  speak: none;
  display: inline-block;
  text-decoration: inherit;
  width: 1em;
  margin-right: .2em;
  text-align: center;
  font-variant: normal;
  text-transform: none;
  line-height: 1em;
  margin-left: .2em;
}
.icon-home:before {
  content: '\e800'; }
.icon-menu:before {
  content: '\e801'; }

/*** Core Superfish Menu Styles ***/
.sf-menu {
  margin: 0;
  padding: 0;
  list-style: none; }
  .sf-menu * {
    margin: 0;
    padding: 0;
    list-style: none; }
  .sf-menu ul {
    position: absolute;
    top: -999em;
    width: 10em;
    /* left offset of submenus need to match (see below) */ }
    .sf-menu ul li {
      width: 100%; }
  .sf-menu li {
    float: left;
    position: relative; }
    .sf-menu li:hover {
      visibility: inherit;
      /* fixes IE7 'sticky bug' */ }
  .sf-menu a {
    display: block;
    position: relative; }
  .sf-menu li:hover ul, .sf-menu li.sfHover ul {
    left: 0;
    top: 2.5em;
    /* match top ul list item height */
    z-index: 99; }

ul.sf-menu li:hover li ul, ul.sf-menu li.sfHover li ul {
  top: -999em; }
ul.sf-menu li li:hover ul, ul.sf-menu li li.sfHover ul {
  left: 10em;
  /* match ul width */
  top: 0; }
ul.sf-menu li li:hover li ul, ul.sf-menu li li.sfHover li ul {
  top: -999em; }
ul.sf-menu li li li:hover ul, ul.sf-menu li li li.sfHover ul {
  left: 10em;
  /* match ul width */
  top: 0; }


/*** Theme Styles **/

body {
  background: #f4f4f4 url("https://s3-us-west-2.amazonaws.com/s.cdpn.io/72900/wpmu001-bg.png") repeat;
  margin: 20px 30px; }
  @media screen and (max-width: 768px) {
    body {
      margin: 0; } }

.wrap {
  width: 100%;
  /* max-width: 1045px;*/
  margin: 0 auto; } 

header.global {
  
  /* Begin modifications to Superfish menu */ }
  header.global .date-search {
    height: 30px;
    background: #fcfcfc;
    border-top: 3px solid #dd374e; }
  header.global .branding {
    background: #2d2d2d;
    height: 137px;
    overflow: none;
    border-top: 4px solid #dd374e; }
    header.global .branding h1 {
      width: 210px;   
      margin: 0; }
    header.global .branding img.logo {
      margin: 18px  10 16px;
      max-width: 80%;}
  header.global nav {
    font-family: "Droid Sans";
    background: #2d2d2d;
    border-top: 4px solid #dd374e;
    /** Bonus - here's how to do a double border ;) **/
    -webkit-box-shadow: 0px 4px 0px 0px #3a3a3a, 0px 8px 0px 0px #dd374e;
    -moz-box-shadow: 0px 4px 0px 0px #3a3a3a, 0px 8px 0px 0px #dd374e;
    box-shadow: 0px 4px 0px 0px #3a3a3a, 0px 8px 0px 0px #dd374e;
    min-height: 40px; }
    header.global nav #hamburger {
      display: none;
      cursor: pointer;
      text-align: center;
      line-height: 46px;
      color: #dddddd; }
      @media screen and (max-width: 768px) {
        header.global nav #hamburger {
          display: block; } }
    header.global nav ul {
      margin: 0;
      padding: 0 25px;
      display: block; }
      @media screen and (max-width: 768px) {
        header.global nav ul {
          display: none;
          margin: 7px 0;
          padding: 0; } }
      header.global nav ul li {
        display: inline-block;
        color: #dddddd;
        line-height: 44px;
        border-right: 1px solid #202020;
        border-left: 1px solid #3a3a3a; }
        @media screen and (max-width: 768px) {
          header.global nav ul li {
            width: 100%;
            background: #2d2d2d;
            border-left: none;
            border-right: none;
            border-top: 1px solid #474747;
            border-bottom: 1px solid #141414; }
            header.global nav ul li:first-child {
              border-top: none; }
            header.global nav ul li:last-child {
              border-bottom: none; } }
        header.global nav ul li:first-child {
          border-left: none; }
        header.global nav ul li:last-child {
          border-right: none; }
        header.global nav ul li:hover {
          color: white; }
          @media screen and (min-width: 768px) {
            header.global nav ul li:hover > a {
              position: relative; }
              header.global nav ul li:hover > a:after {
                content: "";
                position: absolute;
                left: 20px;
                top: 40px;
                border-width: 0 8px 8px;
                border-style: solid;
                border-color: rgba(0, 0, 0, 0) rgba(0, 0, 0, 0) #ef3636;
                display: block;
                width: 0;
                z-index: 999; } }
        header.global nav ul li ul {
          margin-top: 4px;
          background: #2d2d2d;
          border-top: 4px solid #dd374e;
          padding: 0; }
				@media screen and (max-width: 768px) {
          header.global nav ul li ul {
            width: 100% !important;
          }
        }
          header.global nav ul li ul li {
            border-top: 1px solid #474747;
            border-bottom: 1px solid #141414;
            border-right: none;
            border-left: none; }
            header.global nav ul li ul li:first-child {
              border-top: none; }
            header.global nav ul li ul li:last-child {
              border-bottom: none; }
            header.global nav ul li ul li a {
              padding: 10px 15px;
              line-height: 1em; }
            header.global nav ul li ul li:hover {
              padding-left: 5px;
              -webkit-transition-property: all;
              -moz-transition-property: all;
              -o-transition-property: all;
              transition-property: all;
              -webkit-transition-duration: 0.5s;
              -moz-transition-duration: 0.5s;
              -o-transition-duration: 0.5s;
              transition-duration: 0.5s; }
              @media screen and (min-width: 768px) {
                header.global nav ul li ul li:hover a:after {
                  border: none; } }
        header.global nav ul li a {
          text-decoration: none;
          color: #dddddd;
          padding: 0 22px; }
          header.global nav ul li a:hover {
            color: white; }
        header.global nav ul li.home {
          min-width: 46px;
          background: #dd374e;
          border-right: none;
          text-align: center; }
          header.global nav ul li.home span {
            display: none; }
        header.global nav ul li .sub-indicator, header.global nav ul li .top-menu ul li a .sub-indicator {
          right: 7px;
          top: 50%;
          margin-top: -2px;
          position: absolute;
          display: inline-block;
          content: '';
          width: 0;
          height: 0;
          border: 4px solid rgba(0, 0, 0, 0);
          border-top: 4px solid #dddddd; }

</style>