$(document).ready(function(){
    $('.toggle-btn').click(function(){
        var userId = $(this).data('user-id');
        $('#actividades-' + userId).toggle(); // Mostrar/Ocultar la subtabla
    });
});