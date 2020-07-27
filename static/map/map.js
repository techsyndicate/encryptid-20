$('#focus-single').click(function(){
    $('#map1').vectorMap('set', 'focus', {region: 'AU', animate: true});
});

$('#focus-multiple').click(function(){
    $('#map1').vectorMap('set', 'focus', {regions: ['AU', 'JP'], animate: true});
});

$('#focus-coords').click(function(){
    $('#map1').vectorMap('set', 'focus', {scale: 7, lat: 35, lng: 33, animate: true});
});

$('#focus-init').click(function(){
    $('#map1').vectorMap('set', 'focus', {scale: 1, x: 0.5, y: 0.5, animate: true});
});

$('#map').vectorMap({
    map: 'world_mill_en',
    panOnDrag: true,
    backgroundColor: 'black',
    regionsSelectable: false,
    hoverOpacity: 4,
    zoomButtons : true,
    onRegionTipShow: function (e, label, code) {
      e.preventDefault();
    },
    onRegionClick: function(element, code, region){
      let arr = window.location.href.split("/");
      window.location.href = arr[0] + "//" + arr[2] + "/play/" + code;
    },
    regionStyle: {
      initial: {
        "fill": 'black',
        "stroke": "#16e16e",
        "stroke-width": 1,
        "stroke-opacity": 0.5,
      },
      hover: {
        "stroke": "#16e16e",
        "stroke-width": 1.7,
        "stroke-opacity": 3,
      }
    },
    series: {
      regions: [{
        values: {
            // make it light green once 
            // the user completes that level
            US:'red',
            CH:'red',
            GB:'red',
            KW:'red',
            UK:'red',
            JO:'red',
        }
      }]
    }
});