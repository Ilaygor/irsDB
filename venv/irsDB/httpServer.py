from twisted.web import server, resource
from twisted.internet import reactor, defer
import base64


class DummyServer(resource.Resource):
    isLeaf = True

    def returnContent(self, deferred, request, msg):
        print("Finishing request to '%s'" % request.uri)
        request.write(msg)
        request.finish()

    def cancelAnswer(self, err, request, delayedTask):
        print("Cancelling request to '%s': %s" % \
            (request.uri, err.getErrorMessage()))
        delayedTask.cancel()

    def render_GET(self, request):
        print("Received request for '%s'" % request.uri)
        if request.uri == '/delayed':
            print("Delaying answer for '/delayed'")
            d = defer.Deferred()
            delayedTask = reactor.callLater(60, self.returnContent, d,
                                            request, "Hello, delayed world!")
            request.notifyFinish().addErrback(self.cancelAnswer,
                                              request, delayedTask)
            return server.NOT_DONE_YET
        elif request.uri == '/protected':
            auth = request.getHeader('Authorization')
            if auth and auth.split(' ')[0] == 'Basic':
                decodeddata = base64.decodestring(auth.split(' ')[1])
                if decodeddata.split(':') == ['username', 'password']:
                    return "Authorized!"

            request.setResponseCode(401)
            request.setHeader('WWW-Authenticate', 'Basic realm="realmname"')
            return "Authorization required."
        else:
            print("Immediate answering request for '/'")
            return "Hello, world! %s" % request.uri

s = server.Site(DummyServer())
reactor.listenTCP(8888, s)
reactor.run()


