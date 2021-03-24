class PlaylistItem {
  constructor(id, url, thumbnail, title, upvotes, downvotes, timestamp){
    this.id = id;
    this.url = url;
    this.thumbnail = thumbnail;
    this.title = title;
    this.upvotes = upvotes;
    this.downvotes = downvotes;
    this.timestamp = timestamp;
  }

  score(){
    return this.upvotes - this.downvotes;
  }

  toElement(){
    let elem = document.createElement('div');
    elem.classList.add('video');
    elem.innerHTML = `
      <div class="img" style="background-image:url('${ this.thumbnail }')"></div>
      <div class="text-holder">
        <span>${ this.title }</span>
      </div>
      <div class="votes-holder">
        <div class="upvote" onclick="upvote(${ this.id })">${ this.upvotes || 0 }</div>
        <div class="downvote" onclick="downvote(${ this.id })">${ this.downvotes || 0 }</div>
      </div>
    `
    return elem;
  }

  toSuggestion(cb){
    let elem = document.createElement('div');
    elem.classList.add('video');
    elem.innerHTML = `
      <div class="img" style="background-image:url('${ this.thumbnail }')"></div>
      <div class="text-holder">
        <span>${ this.title }</span>
      </div>
    `
    return elem;
  }

  static fromObj(x){
    return new PlaylistItem(x.id, x.url, x.thumbnail, x.title, x.upvotes, x.downvotes, x.timestamp);
  }
}

class Playlist {
  constructor(parentElement){
    this.items = [];
    this.parentElement = parentElement;
  }

  // sort on score then by timestamp
  sort(){
    this.items.sort((x, y) => {
      if(x.score() - y.score() === 0){
        return x.timestamp - y.timestamp;
      } else {
        return y.score() - x.score()
      }
    });
  }

  append(item){
    this.items.push(item);
  }

  redraw(){
    this.sort();
    this.parentElement.innerHTML = '';
    this.items.forEach(item => {
      this.parentElement.appendChild(item.toElement())
    });
  }
}

class SocketEvent {
  constructor(data, message, type){
    this.data = data;
    this.message = message;
    this.type = type;
  }
}
