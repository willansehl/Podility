userid = 0;

window.onload = async function() {
    loadPlaylist()
    userid = get_userid();
    if (userid) {
        open_ws();
        playCurrentVideo();
    }
}

async function loadPlaylist(reload){
  let queue = await fetch('/playlist/0');
  queue = await queue.json();

  if(reload){ $('#left .queue').innerHTML = ""; }

  window.playlist = new Playlist($('#left .queue'));

  queue.playlist.forEach(video => window.playlist.append(PlaylistItem.fromObj(video)));
  window.playlist.redraw();
}

function showVideoSubmit(event){
  $('overlay').style.display = 'block';
  $('#left').style.overflow = 'hidden';
  $('#left').scrollTop = 0;
}

function hideVideoSubmit(event) {
  $('overlay').style.display = 'none';
  $('#left').style.overflow = 'auto';
}

async function upvote(submission_id){
  let vote = await fetch('/submission/'+submission_id+'/upvote?user_id='+userid);
  let vote_result = await vote.json();
  if(vote_result.result == 'already_voted') alert("You already voted on that video!");
  else loadPlaylist(true);
}

async function downvote(submission_id){
  let vote = await fetch('/submission/'+submission_id+'/downvote?user_id='+userid);
  let vote_result = await vote.json()
  if(vote_result.result == 'already_voted') alert("You already voted on that video!");
  else loadPlaylist(true);
}

async function addToPlaylist(id){
  let data = {
    'url': id,
    'start': 0,
    'end': 9999,
    'userid': userid
  };

  let params = {
      method: 'POST',
      mode: 'cors',
      cache: 'no-cache',
      credentials: 'same-origin',
      headers: {'Content-Type': 'application/json'},
      redirect: 'follow',
      referrerPolicy: 'no-referrer',
      body: JSON.stringify(data)
    }

  let response = await fetch('/submission/0', params);
  response = await response.json();
  window.playlist.append(PlaylistItem.fromObj(response));
  window.playlist.redraw();
  hideVideoSubmit(event);
}

async function getYoutubeResults(){
    let query = $('#submitVideoQueryInput').value;

    let response = await fetch('/videoSuggestion?query=' + query);
    response = await response.json();
    $('overlay .suggestions').innerHTML = '';
    response.results.forEach(result => {
      let suggestion = PlaylistItem.fromObj(result).toSuggestion();
      suggestion.onclick = () => {
        $('#submitVideoQueryInput').value = "";
        $('overlay').style.display = 'none';
        addToPlaylist(result.id);
        var input = "submitted " + result.title;

        // todo use SocketEvent
        window.ws.send(input);
        input.value = '';
      }
      $('overlay .suggestions').appendChild(suggestion);
    });
}

function glow(elem){
  if(elem.parentElement.classList[0].startsWith('like')){
    $('.vote-battle .likes').classList.add('glow');
  } else {
    $('.vote-battle .skips').classList.add('glow');
  }
}

function unglow(elem){
  if(elem.parentElement.classList[0].startsWith('like')){
    $('.vote-battle .likes').classList.remove('glow');
  } else {
    $('.vote-battle .skips').classList.remove('glow');
  }
}

function displayMessage(username, message){
  let msgTemplate = `
    <p class="username">${ username }</p>
    <p class="content">${ message }</p>
  `;

  let msg = document.createElement('div');
  msg.classList.add('msg');
  msg.innerHTML = msgTemplate;

  $('#messages').appendChild(msg);
  $('#messages').scrollTop = $('#right').scrollHeight;
}

function open_ws() {
    var client_id = get_userid()
    let connectionString = window.location.protocol.includes('https') ? 'wss://' : 'ws://';
    connectionString += `${document.location.host}/ws/${client_id}`;
    window.users = {};
    window.ws = new WebSocket(connectionString);
    window.ws.onmessage = function (event) {
        var response = JSON.parse(event.data);
        switch(response.type){
          case 'join':
            onUserJoin(response.data.username);
            break;
          case 'leave':
            onUserLeave(response.data.username);
            break;
          case 'chat':
            displayMessage(response.data.username, response.data.message);
            break;
          case 'play':
            playVideo(response.data);
            break;
          case 'pl':
            loadPlaylist(true);
            break;
        }
    };
}

function onUserJoin(username){
  let emojis = ['🥂', '🎉', '🎈', '🍺', '🥳'];
  let emoji = emojis[Math.floor(Math.random()*emojis.length)];
  let color = getRandomUserColor();

  let msg = document.createElement('div');
  msg.classList.add('msg');
  msg.innerHTML = `<p class="username"><span style='color: ${color}'>${ username }</span> has joined ${ emoji }</p>`;

  $('#messages').appendChild(msg);
  $('#messages').scrollTop = $('#right').scrollHeight;
  window.users[username] = {
    'username': username,
    'color': color
  }
}

function onUserLeave(username){
  let emojis = ['😭', '💔'];
  let emoji = emojis[Math.floor(Math.random()*emojis.length)];

  let msg = document.createElement('div');
  msg.classList.add('msg');
  msg.innerHTML = `<p class="username">${ username } has left ${ emoji }</p>`;

  $('#messages').appendChild(msg);
  $('#messages').scrollTop = $('#right').scrollHeight;

  delete window.users[username];
}

function onMessageKeyup(event){
  if(event.code !== 'Enter'){
      return;
  } else {
    sendMessage(event);
  }
}

function sendMessage(event) {
    event.preventDefault();
    var input = document.getElementById("messageText");

    // todo use SocketEvent
    window.ws.send(input.value);
    input.value = '';
}

function onSearchKeyup(event){
  if(event.code !== 'Enter'){
      return;
  } else {
    getYoutubeResults();
  }
}

function receiveMessage(data){
    var messages = document.getElementById('messages');
    var message = document.createElement('section');
    var content = document.createTextNode(data);
    message.appendChild(content);
    messages.appendChild(message);
}

function playVideo(video){
    console.log(video)
    console.log(video.play_from)
    var play_from_str = video.play_from? "&start="+video.play_from : "";
    $("#player").src = "https://www.youtube.com/embed/"+video.yt_id+"?autoplay=1&controls=0"+play_from_str;
    receiveMessage("Now Playing: \""+video.title+"\"");
    loadPlaylist(true);
}

async function playCurrentVideo(){
    let response = await fetch('/getCurrentVideo');
    let video_result = await response.json()
    let video = await video_result.video
    if(video) playVideo(video)
    else $("#video_placeholder").innerText = "No video found!  Please submit a video.";
}

function like(event) {
    event.preventDefault();
    var input = "liked the video";

    // todo use SocketEvent
    window.ws.send(input);
    input.value = '';
}

function skip(event){
  event.preventDefault();
  var input = "liked the video";

  // todo use SocketEvent
  window.ws.send(input);
  input.value = '';
}

function get_userid(){
  var cookie = decodeURIComponent(document.cookie);
  var ca = cookie.split(';');
  for(var i = 0; i <ca.length; i++) {
      var c = ca[i].trim();
      if(c.startsWith('userid')){
        uid = c.split("=")[1];
        if(uid != 'undefined') {
          console.log(uid);
          return uid;
        }
      }
  }
  open_user_overlay();
  return 0;
}

function open_user_overlay(){
  $('.overlay').style.display = "block";
}

async function submit_user(){
  let data = {
    'username': $('#username').value,
    'display_name': $('#display_name').value
  };

  let params = {
      method: 'POST',
      mode: 'cors',
      cache: 'no-cache',
      credentials: 'same-origin',
      headers: {'Content-Type': 'application/json'},
      redirect: 'follow',
      referrerPolicy: 'no-referrer',
      body: JSON.stringify(data)
    }

  let response = await fetch('/createUser', params)
      .then(response => response.json())
      .then(data => {
          console.log();
          console.log(data);
        uid = data['userid'];
        console.log("uid is " + uid)
        set_cookie(uid);
        userid = uid;
        $('.overlay').style.display = "none";
        open_ws();
        playCurrentVideo();
      });
}

function set_cookie(userid){
  document.cookie = 'userid='+userid
}


//////////// utility functions ////////////

function $(str){
  return document.querySelector(str);
}

function wait(ms){
  return new Promise(r => setTimeout(r, ms));
}

function getRandomUserColor(){
  let h = Math.floor(Math.random()*360);
  return `hsl(${h} 100% 80%)`;
}
