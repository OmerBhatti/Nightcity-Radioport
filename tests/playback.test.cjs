const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const html = fs.readFileSync(require('node:path').join(__dirname, '../index.html'), 'utf8');
const script = html.match(/<script>([\s\S]*?)<\/script>/)[1];
new Function(script);
function player() {
  const context = vm.createContext({assert});
  vm.runInContext(`
    const window = {}; const calls = [];
    const uriA = 'spotify:track:' + 'A'.repeat(22), uriB = 'spotify:track:' + 'B'.repeat(22);
    const validUri = uri => typeof uri === 'string' && /^spotify:track:[A-Za-z0-9]{22}$/.test(uri);
    let cursor = 0, active = null, pendingUri = null, initializing = false, playerReady = true;
    let api = null, queue = [], trackIndex = 0, awaitingStart = true, autoPlayPending = false;
    const stations = [{station_name:'TEST',tracks:[{uri:null},{uri:uriA},{uri:uriB}]}, {station_name:'NO STATION',tracks:[]}];
    let controller = {loadUri:uri=>calls.push(uri),play:()=>{},pause:()=>calls.push('pause'),resume:()=>calls.push('resume')};
    let loading = false;
    function setLoading(value) { loading = value; }
    function updateTrackControls() {}
    function setPlaybackState() {}
    function showTrack() {} function status() {}
  ` + script.slice(script.indexOf('function playCurrentTrack()'), script.indexOf('function togglePlayerControls(')), context);
  return code => vm.runInContext(code, context);
}
test('selection starts first valid track and skips missing URIs', () => {
  player()(`selectStation(); assert.equal(queue.length,2); assert.equal(calls[0],uriA);`);
});
test('completion advances in order, ignores stale events, and loops', () => {
  player()(`
    selectStation();
    const update=(uri,position)=>handlePlaybackUpdate({data:{playingURI:uri,duration:1000,position,isPaused:false,isBuffering:false}});
    update(uriA,100); update(uriA,1000); assert.equal(pendingUri,uriB);
    update(uriA,1000); assert.equal(calls.length,2);
    update(uriB,100); update(uriB,1000); assert.equal(pendingUri,uriA);
  `);
});
test('one-song loop advances once until playback restarts', () => {
  player()(`
    stations[0].tracks=[{uri:uriA}]; selectStation();
    const update=position=>handlePlaybackUpdate({data:{playingURI:uriA,duration:1000,position,isPaused:false,isBuffering:false}});
    update(100); update(1000); update(1000); assert.equal(calls.length,2);
    update(100); update(1000); assert.equal(calls.length,3);
  `);
});
test('NO STATION clears queue and ignores delayed completion', () => {
  player()(`selectStation(); cursor=1; selectStation();
    handlePlaybackUpdate({data:{playingURI:uriA,duration:1000,position:1000}});
    assert.equal(queue.length,0); assert.equal(calls.at(-1),'pause');`);
});
test('selecting the current station resumes instead of restarting', () => {
  player()(`selectStation(); selectStation(); assert.equal(calls.at(-1),'resume');`);
});

test('repeated Spotify ready events do not reload or replay the track', () => {
  player()(`
    const listeners = {};
    const embed = {addListener:(name,fn)=>listeners[name]=fn,loadUri:uri=>calls.push(uri),play:()=>calls.push('play'),pause:()=>{}};
    const $ = () => ({});
    controller=null; playerReady=false;
    api={createController:(element,options,callback)=>callback(embed)};
    selectStation(); listeners.ready(); listeners.ready(); listeners.ready();
    assert.deepEqual(calls,['play']);
  `);
});
test('changing channel before ready loads the latest selection only once', () => {
  player()(`
    const listeners = {};
    const embed = {addListener:(name,fn)=>listeners[name]=fn,loadUri:uri=>calls.push(uri),play:()=>calls.push('play'),pause:()=>{}};
    const $ = () => ({});
    controller=null; playerReady=false;
    api={createController:(element,options,callback)=>callback(embed)};
    selectStation();
    stations.push({station_name:'OTHER',tracks:[{uri:uriB}]}); cursor=2; selectStation();
    listeners.ready(); listeners.ready(); assert.deepEqual(calls,[uriB,'play']);
  `);
});
test('turning radio off before ready prevents autoplay', () => {
  player()(`
    const listeners = {};
    const embed = {addListener:(name,fn)=>listeners[name]=fn,loadUri:()=>{},play:()=>calls.push('play'),pause:()=>calls.push('pause')};
    const $ = () => ({});
    controller=null; playerReady=false;
    api={createController:(element,options,callback)=>callback(embed)};
    selectStation(); cursor=1; selectStation(); listeners.ready();
    assert.ok(!calls.includes('play'));
  `);
});

test('previous and next wrap through only the active channel', () => {
  player()(`selectStation(); previousTrack(); assert.equal(pendingUri,uriB);
    nextTrack(); assert.equal(pendingUri,uriA); nextTrack(); assert.equal(pendingUri,uriB);`);
});
test('loading follows connecting, buffering and playing states', () => {
  player()(`selectStation(); assert.equal(loading,true);
    handlePlaybackUpdate({data:{playingURI:uriA,isPaused:false,isBuffering:false,position:100,duration:1000}});
    assert.equal(loading,false);
    handlePlaybackUpdate({data:{playingURI:uriA,isPaused:false,isBuffering:true,position:200,duration:1000}});
    assert.equal(loading,true);
    cursor=1; selectStation(); assert.equal(loading,false);
  `);
});
test('stale playback events do not dismiss a new song loading overlay', () => {
  player()(`selectStation(); nextTrack();
    handlePlaybackUpdate({data:{playingURI:uriA,isBuffering:false}});
    assert.equal(loading,true); assert.equal(pendingUri,uriB);`);
});
test('song navigation with an empty queue does nothing', () => {
  player()(`previousTrack(); nextTrack(); assert.equal(calls.length,0);`);
});
test('saved channel is restored by frequency after the station list changes order', () => {
  player()(`
    stations[0].station_num='89.7'; stations[1].station_num='';
    const localStorage={values:new Map(),setItem(key,value){this.values.set(key,value)},getItem(key){return this.values.get(key) ?? null}};
    selectStation(); stations.reverse(); assert.equal(initialStationIndex(),1);
    cursor=0; selectStation(); assert.equal(initialStationIndex(),0);
  `);
});
test('malformed or removed saved channels fall back to a playable station', () => {
  player()(`
    stations[0].station_num='89.7';
    const localStorage={value:'bad JSON',getItem(){return this.value}};
    assert.equal(initialStationIndex(),0);
    localStorage.value=JSON.stringify({station_num:'100.0'});
    assert.equal(initialStationIndex(),0);
  `);
});
test('unavailable local storage does not interrupt playback or initialization', () => {
  player()(`
    const localStorage={setItem(){throw Error('blocked')},getItem(){throw Error('blocked')}};
    selectStation(); assert.equal(calls[0],uriA); assert.equal(initialStationIndex(),0);
  `);
});

test('last song restores by URI after refresh and playlist reordering', () => {
  player()(`
    const localStorage={values:new Map(),setItem(key,value){this.values.set(key,value)},getItem(key){return this.values.get(key) ?? null}};
    selectStation(); nextTrack(); assert.equal(pendingUri,uriB);
    active=null; queue=[]; trackIndex=0;
    stations[0].tracks.reverse(); selectStation();
    assert.equal(pendingUri,uriB); assert.equal(trackIndex,0);
  `);
});
test('each channel remembers its own track and falls back if a track is removed', () => {
  player()(`
    const localStorage={values:new Map(),setItem(key,value){this.values.set(key,value)},getItem(key){return this.values.get(key) ?? null}};
    stations.push({station_name:'OTHER',tracks:[{uri:uriA},{uri:uriB}]});
    selectStation(); nextTrack();
    cursor=2; selectStation(); assert.equal(pendingUri,uriA);
    cursor=0; selectStation(); assert.equal(pendingUri,uriB);
    cursor=2; selectStation();
    stations[0].tracks=[{uri:uriA}];cursor=0;selectStation();
    assert.equal(pendingUri,uriA);
  `);
});
test('automatic advancement saves the next song', () => {
  player()(`
    const localStorage={values:new Map(),setItem(key,value){this.values.set(key,value)},getItem(key){return this.values.get(key) ?? null}};
    selectStation();
    handlePlaybackUpdate({data:{playingURI:uriA,isPaused:false,isBuffering:false,position:100,duration:1000}});
    handlePlaybackUpdate({data:{playingURI:uriA,isPaused:false,isBuffering:false,position:1000,duration:1000}});
    assert.equal(localStorage.getItem(savedTrackKey()),uriB);
  `);
});

test('next song requests autoplay after load readiness without reloading again', () => {
  player()(`
    const listeners = {};
    const embed = {addListener:(name,fn)=>listeners[name]=fn,loadUri:uri=>calls.push(uri),play:()=>calls.push('play'),pause:()=>{}};
    const $ = () => ({});
    controller=null; playerReady=false;
    api={createController:(element,options,callback)=>callback(embed)};
    selectStation(); listeners.ready();
    nextTrack(); listeners.ready(); listeners.ready();
    assert.deepEqual(calls,['play',uriB,'play','play']);
  `);
});
test('pausing in the middle of a song does not skip to another song', () => {
  player()(`selectStation();
    handlePlaybackUpdate({data:{playingURI:uriA,isPaused:false,isBuffering:false,position:100,duration:1000}});
    handlePlaybackUpdate({data:{playingURI:uriA,isPaused:true,isBuffering:false,position:500,duration:1000}});
    assert.equal(pendingUri,uriA); assert.equal(trackIndex,0);
  `);
});
