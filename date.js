//jshint esversio:6

exports.getDate = function () {   //module.exports. can be written s exports. as short

    const today = new Date();

    const options = {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    };

    return day = today.toLocaleDateString("en-US", options);

}


exports.getDay = function getDay() {
    const today = new Date();

    const options = {
        weekday: 'long'
    };

    return day = today.toLocaleDateString("en-US", options);


}

console.log(module.exports);