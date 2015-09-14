$(document).ready( function() {
  
  $('#languages tr').each( function() {
    this.faults = 0;
  });

  $('#chooser span').attr( 'unselectable', 'on');

  $('#chooser span[f="-3"]').hide();
  $('#chooser span.rare').hide();

  $('#scroller').click( function() {
    $('html, body').animate({
      scrollTop: $('#chooser').offset().top
    }, 500);
  });

  function handle_click( span) {
    if( span != null) {
      var o = $(span);
      var oi = o.attr( 'f');
      if( oi == '-1') {  // reset
        $('#languages tr').each( function() {
          this.faults = 0;
        });
        $('#chooser span').each( function() {
          $(this).removeClass("yes no");
        });
      } else if( oi == '-2') {  // toggle rare phonemes
        $('#chooser span[f="-2"]').hide();
        $('#chooser span[f="-3"]').show();
        $('#chooser span.rare').show();
      } else if( oi == '-3') {  // toggle rare phonemes
        $('#chooser span[f="-3"]').hide();
        $('#chooser span[f="-2"]').show();
        $('#chooser span.rare').hide();
        $('#chooser span.rare').each( function() {
          var o = $(this)
          var oi = o.attr( 'f');
          if( o.hasClass( 'yes')) {
            o.removeClass( 'yes')
            $('#languages tr').each( function() {
              if( $(this).attr( 'f'+oi) == undefined) {
                this.faults -= 1;
              }
            });
          } else if( o.hasClass( 'no')) {
            o.removeClass( 'no')
            $('#languages tr').each( function() {
              if( $(this).attr( 'f'+oi) != undefined) {
                this.faults -= 1;
              }
            });
          }
        });
      } else if( o.hasClass( 'no')) {
        o.removeClass( 'no');

        $('#languages tr').each( function() {
          if( $(this).attr( 'f'+oi) != undefined) {
            this.faults -= 1;
          }
        });
      } else if( o.hasClass( 'yes')) {
        o.removeClass( 'yes');
        o.addClass( 'no');

        $('#languages tr').each( function() {
          if( $(this).attr( 'f'+oi) == undefined) {
            this.faults -= 1;
          } else {
            this.faults += 1;
          }
        });
      } else {
        o.addClass( 'yes');

        $('#languages tr').each( function() {
          if( $(this).attr( 'f'+oi) == undefined) {
            this.faults += 1;
          }
        });
      }
    }

    /*
    $('div#selections').html(
      $('#chooser span.yes').map( function() {
	return $(this).attr( 'f');
      }).get().join(",") + ';' +
      $('#chooser span.no').map( function() {
	return $(this).attr( 'f');
      }).get().join(",") + ';' +
      $('#languages div').map( function() {
	return '' + this.faults;
      }).get().join(",")
    );
    */

    var matches = 0;
    $('#languages tr').each( function() {
      if( this.faults == 0) {
        $(this).css('display', 'block')
        matches += 1;
      } else {
        $(this).css('display', 'none')
      }
    });
    $('#languages span.key').html( '' + matches)
  }

  $('#chooser span').click( function( e) { 
    handle_click( this); 
    // e.stopPropagation();
  });
  handle_click( null);
  
});
