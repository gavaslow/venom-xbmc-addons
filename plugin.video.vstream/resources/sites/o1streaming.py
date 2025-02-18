# -*- coding: utf-8 -*-
# vStream https://github.com/Kodi-vStream/venom-xbmc-addons

import re

from resources.lib.gui.hoster import cHosterGui
from resources.lib.gui.gui import cGui
from resources.lib.handler.inputParameterHandler import cInputParameterHandler
from resources.lib.handler.outputParameterHandler import cOutputParameterHandler
from resources.lib.handler.requestHandler import cRequestHandler
from resources.lib.parser import cParser
from resources.lib.comaddon import progress

SITE_IDENTIFIER = 'o1streaming'
SITE_NAME = '01 Streaming'
SITE_DESC = 'Films & Séries'

URL_MAIN = 'https://01streaming.tv/'

FUNCTION_SEARCH = 'showMovies'
URL_SEARCH = (URL_MAIN + '?s=', 'showMovies')
URL_SEARCH_MOVIES = (URL_SEARCH[0], 'showMovies')
URL_SEARCH_SERIES = (URL_SEARCH[0], 'showMovies')

MOVIE_NEWS = (URL_MAIN + 'films-en-streaming/', 'showMovies')
MOVIE_GENRES = ('?type=movies', 'showGenres')
MOVIE_ANNEES = (True, 'showMovieYears')

SERIE_NEWS = (URL_MAIN + 'series-streaming/', 'showMovies')
SERIE_GENRES = ('?type=series', 'showGenres')


def load():
    oGui = cGui()

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', 'http://venom/')
    oGui.addDir(SITE_IDENTIFIER, 'showSearch', 'Recherche', 'search.png', oOutputParameterHandler)

    oOutputParameterHandler.addParameter('siteUrl', MOVIE_NEWS[0])
    oGui.addDir(SITE_IDENTIFIER, MOVIE_NEWS[1], 'Films (Derniers ajouts)', 'films.png', oOutputParameterHandler)

    oOutputParameterHandler.addParameter('siteUrl', MOVIE_GENRES[0])
    oGui.addDir(SITE_IDENTIFIER, MOVIE_GENRES[1], 'Films (Genres)', 'genres.png', oOutputParameterHandler)

    oOutputParameterHandler.addParameter('siteUrl', MOVIE_ANNEES[0])
    oGui.addDir(SITE_IDENTIFIER, MOVIE_ANNEES[1], 'Films & Séries (Par années)', 'annees.png', oOutputParameterHandler)

    oOutputParameterHandler.addParameter('siteUrl', SERIE_NEWS[0])
    oGui.addDir(SITE_IDENTIFIER, SERIE_NEWS[1], 'Séries (Derniers ajouts)', 'series.png', oOutputParameterHandler)

    oOutputParameterHandler.addParameter('siteUrl', SERIE_GENRES[0])
    oGui.addDir(SITE_IDENTIFIER, SERIE_GENRES[1], 'Séries (Genres)', 'genres.png', oOutputParameterHandler)

    oGui.setEndOfDirectory()


def showMovieYears():
    oGui = cGui()
    oRequestHandler = cRequestHandler(URL_MAIN + 'accueil/')
    sHtmlContent = oRequestHandler.request()

    sPattern = 'class="btn sm" href="([^"]+)">([^<]+)'
    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, sPattern)

    if (aResult[0] == True):
        oOutputParameterHandler = cOutputParameterHandler()
        for aEntry in reversed(aResult[1]):
            sUrl = aEntry[0]
            Year = aEntry[1]

            oOutputParameterHandler.addParameter('siteUrl', sUrl)
            oGui.addDir(SITE_IDENTIFIER, 'showMovies', Year, 'annees.png', oOutputParameterHandler)

    oGui.setEndOfDirectory()


def showGenres():
    oGui = cGui()

    oInputParameterHandler = cInputParameterHandler()
    siteUrl = oInputParameterHandler.getValue('siteUrl')

    oRequestHandler = cRequestHandler(URL_MAIN + 'accueil/')
    sHtmlContent = oRequestHandler.request()

    sPattern = '<li class="cat-item cat-item-.+?href="([^"]+)">([^<]+)<'
    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, sPattern)

    if (aResult[0] == True):
        oOutputParameterHandler = cOutputParameterHandler()
        for aEntry in aResult[1]:
            sUrl = aEntry[0] + siteUrl
            sTitle = aEntry[1]

            oOutputParameterHandler.addParameter('siteUrl', sUrl)
            oGui.addDir(SITE_IDENTIFIER, 'showMovies', sTitle, 'genres.png', oOutputParameterHandler)

    oGui.setEndOfDirectory()


def showSearch():
    oGui = cGui()
    sSearchText = oGui.showKeyBoard()
    if (sSearchText != False):
        sUrl = URL_SEARCH[0] + sSearchText.replace(' ', '%20')
        showMovies(sUrl)
        oGui.setEndOfDirectory()
        return


def showMovies(sSearch=''):
    oGui = cGui()

    oInputParameterHandler = cInputParameterHandler()
    sUrl = oInputParameterHandler.getValue('siteUrl')
    if sSearch:
        sUrl = sSearch

    oRequestHandler = cRequestHandler(sUrl)
    sHtmlContent = oRequestHandler.request()
    sPattern = 'class="entry-header"><h2 class="entry-title">([^<>]+).+?src="([^"]+).+?class="year">([^<]+)<.+?<a href="([^"]+)"'
    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, sPattern)

    if (aResult[0] == True):
        total = len(aResult[1])
        progress_ = progress().VScreate(SITE_NAME)
        oOutputParameterHandler = cOutputParameterHandler()
        for aEntry in aResult[1]:
            progress_.VSupdate(progress_, total)
            if progress_.iscanceled():
                break

            sThumb = aEntry[1]
            if sThumb.startswith('//'):
                sThumb = 'http:' + sThumb
            sYear = aEntry[2]
            sUrl2 = aEntry[3]
            sTitle = aEntry[0]

            s = sTitle
            if ('/release/' in sUrl or sSearch):
                if '/serie' in sUrl2:
                    s = s + ' [Série] '
                else:
                    s = s + ' [Film] '

            sDisplayTitle = s
            if sYear:
                sDisplayTitle += '(%s)' % sYear

            oOutputParameterHandler.addParameter('siteUrl', sUrl2)
            oOutputParameterHandler.addParameter('sMovieTitle', sTitle)
            oOutputParameterHandler.addParameter('sThumb', sThumb)
            oOutputParameterHandler.addParameter('sYear', sYear)

            if '/serie' in sUrl2:
                oGui.addTV(SITE_IDENTIFIER, 'showSaisons', sDisplayTitle, 'series.png', sThumb, '', oOutputParameterHandler)
            else:
                oGui.addMovie(SITE_IDENTIFIER, 'showLinks', sDisplayTitle, 'films.png', sThumb, '', oOutputParameterHandler)

        progress_.VSclose(progress_)

    if not sSearch:
        sNextPage, sPaging = __checkForNextPage(sHtmlContent)
        if (sNextPage != False):
            oOutputParameterHandler = cOutputParameterHandler()
            oOutputParameterHandler.addParameter('siteUrl', sNextPage)
            oGui.addNext(SITE_IDENTIFIER, 'showMovies', 'Page ' + sPaging, oOutputParameterHandler)
        oGui.setEndOfDirectory()


def __checkForNextPage(sHtmlContent):
    oParser = cParser()
    sPattern = '>([^<]+)</a><a href="([^"]+)"\s*>SUIVANT</a>'
    aResult = oParser.parse(sHtmlContent, sPattern)
    if (aResult[0] == True):
        sNumberMax = aResult[1][0][0]
        sNextPage = aResult[1][0][1]
        sNumberNext = re.search('/page/([0-9]+)', sNextPage).group(1)
        sPaging = sNumberNext + '/' + sNumberMax
        if sNextPage.startswith('/'):
            return URL_MAIN[:-1] + sNextPage, sPaging
        else:
            return sNextPage, sPaging

    return False, 'none'


def showSaisons():
    oGui = cGui()
    oParser = cParser()
    oInputParameterHandler = cInputParameterHandler()
    sUrl = oInputParameterHandler.getValue('siteUrl')
    sMovieTitle = oInputParameterHandler.getValue('sMovieTitle')
    sThumb = oInputParameterHandler.getValue('sThumb')

    oRequestHandler = cRequestHandler(sUrl)
    sHtmlContent = oRequestHandler.request()
    sDesc = ''
    sPattern = 'class="description.+?<p>(.+?)<.p><.div>'
    aResult = oParser.parse(sHtmlContent, sPattern)
    if (aResult[0] == True):
        sDesc = aResult[1][0]
        sDesc = ('[I][COLOR grey]%s[/COLOR][/I] %s') % ('Synopsis : ', sDesc)

    sPattern = 'choose-season.+?ref="([^"]+).+?inline">([^<]+)'
    aResult = oParser.parse(sHtmlContent, sPattern)

    if (aResult[0] == True):
        oOutputParameterHandler = cOutputParameterHandler()
        for aEntry in aResult[1]:
            sUrl2 = aEntry[0]
            saison = aEntry[1]

            sTitle = ("%s %s") % (sMovieTitle, ' Saison ' + saison)

            oOutputParameterHandler.addParameter('siteUrl', sUrl2)
            oOutputParameterHandler.addParameter('sThumb', sThumb)
            oOutputParameterHandler.addParameter('sDesc', sDesc)
            oOutputParameterHandler.addParameter('sMovieTitle', sMovieTitle)
            oGui.addSeason(SITE_IDENTIFIER, 'ShowEpisodes', sTitle, '', sThumb, sDesc, oOutputParameterHandler)

    oGui.setEndOfDirectory()


def ShowEpisodes():
    oGui = cGui()
    oParser = cParser()
    oInputParameterHandler = cInputParameterHandler()
    sUrl = oInputParameterHandler.getValue('siteUrl')
    sThumb = oInputParameterHandler.getValue('sThumb')
    sDesc = oInputParameterHandler.getValue('sDesc')

    oRequestHandler = cRequestHandler(sUrl)
    sHtmlContent = oRequestHandler.request()

    sPattern = '<h2 class="entry-title">([^><]+).+?<a href="([^"]+)" class="lnk-blk">'
    aResult = oParser.parse(sHtmlContent, sPattern)

    if (aResult[0] == True):
        oOutputParameterHandler = cOutputParameterHandler()
        for aEntry in aResult[1]:
            sUrl2 = aEntry[1]
            sTitle = aEntry[0].replace('- Saison', 'Saison')

            oOutputParameterHandler.addParameter('siteUrl', sUrl2)
            oOutputParameterHandler.addParameter('sMovieTitle', sTitle)
            oOutputParameterHandler.addParameter('sThumb', sThumb)
            oOutputParameterHandler.addParameter('sDesc', sDesc)
            oGui.addEpisode(SITE_IDENTIFIER, 'showLinks', sTitle, '', sThumb, sDesc, oOutputParameterHandler)

    oGui.setEndOfDirectory()


def showLinks():
    oGui = cGui()
    oInputParameterHandler = cInputParameterHandler()
    sUrl = oInputParameterHandler.getValue('siteUrl')
    sMovieTitle = oInputParameterHandler.getValue('sMovieTitle')
    sThumb = oInputParameterHandler.getValue('sThumb')
    sDesc = oInputParameterHandler.getValue('sDesc')

    oRequestHandler = cRequestHandler(sUrl)
    sHtmlContent = oRequestHandler.request()
    oParser = cParser()

    numUrl = 0
    sPatternUrl = '<iframe (?:data-)*src="([^"]+)"'
    aResultUrl = oParser.parse(sHtmlContent, sPatternUrl)
    if (aResultUrl[0] == True):
        sPatternHost = '<a class="btn(| on)" href="(.+?)".+?<span class="server">([^<]+) <'
        aResultHost = oParser.parse(sHtmlContent, sPatternHost)
        if (aResultHost[0] == True):
            oOutputParameterHandler = cOutputParameterHandler()
            for aEntry in aResultHost[1]:
                sUrl2 = aResultUrl[1][numUrl]
                numUrl += 1
                sHost = aEntry[2]
                sLang = 'VF'
                if '-VOSTFR' in sHost:
                    sLang = 'VOSTFR'
                sHost = sHost.replace('VF', '').replace('VOSTFR', '')
                
                oHoster = cHosterGui().checkHoster(sHost)
                if (oHoster != False):
                    sDisplayTitle = ('%s [COLOR coral]%s[/COLOR] (%s)') % (sMovieTitle, sHost, sLang)
                    oOutputParameterHandler.addParameter('siteUrl', sUrl2)
                    oOutputParameterHandler.addParameter('sThumb', sThumb)
                    oOutputParameterHandler.addParameter('sDesc', sDesc)
                    oOutputParameterHandler.addParameter('sHost', sHost)
                    oOutputParameterHandler.addParameter('sLang', sLang)
                    oOutputParameterHandler.addParameter('sMovieTitle', sMovieTitle)
                    oGui.addLink(SITE_IDENTIFIER, 'showHosters', sDisplayTitle, sThumb, '', oOutputParameterHandler)

    oGui.setEndOfDirectory()

def showHosters():
    oGui = cGui()
    oInputParameterHandler = cInputParameterHandler()
    sUrl = oInputParameterHandler.getValue('siteUrl')
    sMovieTitle = oInputParameterHandler.getValue('sMovieTitle')
    sThumb = oInputParameterHandler.getValue('sThumb')

    oRequestHandler = cRequestHandler(sUrl)
    sHtmlContent = oRequestHandler.request()
    oParser = cParser()
    sPattern = '<iframe.+?src="([^"]+)"'
    aResult = oParser.parse(sHtmlContent, sPattern)

    if (aResult[0] == True):
        for aEntry in aResult[1]:

            sHosterUrl = aEntry
            if sHosterUrl.startswith('/'):
                sHosterUrl = 'http:' + sHosterUrl

            oHoster = cHosterGui().checkHoster(sHosterUrl)
            if (oHoster != False):
                oHoster.setDisplayName(sMovieTitle)
                oHoster.setFileName(sMovieTitle)
                cHosterGui().showHoster(oGui, oHoster, sHosterUrl, sThumb)

    oGui.setEndOfDirectory()
