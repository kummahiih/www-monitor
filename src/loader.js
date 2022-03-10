var page = new WebPage(),
    t, address, output, contentfilename, size;

if (phantom.args.length !== 2) {
    console.log('Usage: load.js <some URL> <renderoutputfilename>');
    phantom.exit();
} else {
    t = Date.now();
    address = phantom.args[0];
    output = phantom.args[1];
    page.viewportSize = { width: 600, height: 600 };

    console.log('adress: ' + address)
    console.log('render output file: ' + output)

    page.open(address, function (status) {
	console.log('Status: ' + status)
        t = Date.now() - t;
        console.log('Loading time ' + t + ' msec');
        if (status !== 'success') {
            console.log('FAIL to load the address');
            phantom.exit();
        } else {
            console.log('Loading OK.');
        
	window.setTimeout(function () {
                try{
                    page.render(output);
                    console.log('Rendering OK.');
                } catch (e) {
                    console.log('Rendering FAIL: ' +e);
                }
                //implement a function (at qt side) for this and or find a better way to implement this...
                //see: http://code.google.com/p/phantomjs/issues/detail?id=129
                console.log('Page content:');
                console.log('------8<----8<--------8<---');
                console.log(page.content);
                
                phantom.exit();
            }, 200);
        }
    });
}
