function trim(txt) {
    if (txt.length < 65) return txt;
    return txt.substring(0, 63) + "...";
}

function update_context() {
    // Get context at window top.
    var t = $(window).scrollTop(),
        context = [null, null, null],
        dontshow = false;

    $('h2,h3,h4').each(function() {
        if ($(this).offset().top + $(this).height() < t) {
            // H2,H3,H4 => 0,1,2
            var lvl = parseInt(this.tagName.substring(1), 10) - 2;
            context[lvl] = $(this).text();
            for (var i = lvl+1; i < 4; i++) // clear levels within until we encounter them
            context[i] = null;
        } else if ($(this).offset().top < t+$('#context').height()*1.2) {
            dontshow = true;
        }
    });

    if ($('#context').css( 'position' ) !== 'fixed')
        $('#context').css({ position: 'absolute', top: t }); // should not do if fixed is supported
    if (!context[0] || dontshow) {
        $('#context').fadeOut();
    } else {
        $('#context .container').text('');
        for (var i = 0; i < context.length; i++) {
            if (!context[i]) break;
            $('#context .container').append($('<div/>').text(trim(context[i])));
        }
        $('#context').fadeIn();
    }
}

$(function() {
    $(window).scroll(update_context);
});
