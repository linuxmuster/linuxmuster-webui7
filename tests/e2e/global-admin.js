var auth = require('./authconfig.json');

describe('lmn landingpage connect', function() {
    it('should show the loading page as global-admin', function() {
        browser.get(auth.url);

        element(by.model('username')).sendKeys(auth.admin.login);
        element(by.model('password')).sendKeys(auth.admin.pw);
        element(by.css('a[ng\\:click^="login"]')).click();
        browser.sleep(8000);
        expect(element.all(by.tagName('h2')).first().getText()).toContain('Linuxmuster.net 7');
    });
});

describe('lmn disconnect', function() {
    it('should show the login page again', function() {
        element(by.css('a[uib-dropdown-toggle]')).click();
        element(by.css('a[ng\\:click^="identity.logout"]')).click();
        browser.sleep(5000);
        expect(element.all(by.tagName('input')).first().getAttribute('ng:model')).toContain('username');
    });
});

// Define an array with a lot of users for your environment test in ./authconfig.json
// // "testlogin": ["testuser", ...],
// describe('lmn monster connect', function() {
//     it('should connect and disconnect 1000 times', function() {
//         for(var i=0; i < 1000; i++){
//             browser.get(auth.url);
//             element(by.model('username')).sendKeys(auth.testlogin[i % auth.testlogin.length]);
//             element(by.model('password')).sendKeys("Muster!");
//             element(by.css('a[ng\\:click^="login"]')).click();
//             browser.sleep(6000);
//             element(by.css('a[uib-dropdown-toggle]')).click();
//             element(by.css('a[ng\\:click^="identity.logout"]')).click();
//             browser.sleep(4000);
//         };
//         // Just try the last logout :
//         expect(element.all(by.tagName('input')).first().getAttribute('ng:model')).toContain('username');
//     });
// });
