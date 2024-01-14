from django.shortcuts import render, redirect
from .forms import Accidente_TransitoForm
from apps.Gestionar_Evidencia.forms import imageform, videoform, audioform
from .models import Accidente_Transito
from apps.Gestionar_Evidencia.models import MyImage, MyVideo, MyAudio
from rest_framework import generics
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.generic.edit import FormView
from django.contrib.auth.forms import AuthenticationForm
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import AccidenteSerializer
from django.contrib import messages
import datetime


class AccidenteList(generics.ListCreateAPIView):
    queryset = Accidente_Transito.objects.all()
    serializer_class = AccidenteSerializer
    permission_classes = (IsAuthenticated,)
    authentication_class = (TokenAuthentication,)


def crearAccidente_Transito(request):

    NumeroAccidente = request.POST.get('NumeroAccidente')
    TipoAccidente = request.POST.get('TipoAccidente')
    fechaInicio = request.POST.get('FechaInicio')
    fechaFin = request.POST.get('FechaFin')

    if str(NumeroAccidente)+'' != '': 
        try:
             accidentes = Accidente_Transito.objects.filter(pk=NumeroAccidente)
             contador = Accidente_Transito.objects.filter(pk=NumeroAccidente).count()
             return render(request, 'Gestionar_Accidente/crear_accidente_transito.html', {'accidentes': accidentes, 'contador': contador})
        except Accidente_Transito.DoesNotExist:
             messages.warning(request, 'No se encontraron coincidencias')
             return render(request, 'Gestionar_Accidente/crear_accidente_transito.html')
    elif (str(fechaFin)+'' != '') & (str(fechaInicio)+'' != ''):
        try:

            if str(TipoAccidente)+'' == 'Todos':
                accidentes = Accidente_Transito.objects.all().filter(Fecha__gte=fechaInicio, Fecha__lte=fechaFin)
                contador = Accidente_Transito.objects.filter(Fecha__gte=fechaInicio, Fecha__lte=fechaFin).count()
            else:
                accidentes = Accidente_Transito.objects.all().filter(Fecha__gte=fechaInicio, Fecha__lte=fechaFin, TipoAccidente=TipoAccidente)
                contador = Accidente_Transito.objects.filter(Fecha__gte=fechaInicio, Fecha__lte=fechaFin, TipoAccidente=TipoAccidente).count()

            return render(request, 'Gestionar_Accidente/crear_accidente_transito.html', {'accidentes': accidentes, 'contador': contador})
        except Accidente_Transito.DoesNotExist:
            messages.warning(request, 'No se encontraron coincidencias')
            return render(request, 'Gestionar_Accidente/crear_accidente_transito.html')

    else:
        messages.warning(request, 'Ingrese NumeroAccidente')
        return render(request, 'Gestionar_Accidente/crear_accidente_transito.html')


def crearAccidente_Transito_juez(request):

    NumeroAccidente = request.POST.get('NumeroAccidente')
    TipoAccidente = request.POST.get('TipoAccidente')
    fechaInicio = request.POST.get('FechaInicio')
    fechaFin = request.POST.get('FechaFin')

    if str(NumeroAccidente)+'' != '':
        try:
            accidentes = Accidente_Transito.objects.filter(pk=NumeroAccidente)
            contador = Accidente_Transito.objects.filter(pk=NumeroAccidente).count()
            return render(request, 'Gestionar_Accidente/crear_accidente_transito_juez.html', {'accidentes': accidentes, 'contador': contador})
        except Accidente_Transito.DoesNotExist:
            messages.warning(request, 'No se encontraron coincidencias')
            return render(request, 'Gestionar_Accidente/crear_accidente_transito_juez.html')
    
    elif (str(fechaFin)+'' != '') & (str(fechaInicio)+'' != ''):
        try:
            
            if str(TipoAccidente)+'' == 'Todos':
                accidentes = Accidente_Transito.objects.all().filter(Fecha__gte=fechaInicio, Fecha__lte=fechaFin)
                contador = Accidente_Transito.objects.filter(Fecha__gte=fechaInicio, Fecha__lte=fechaFin).count()
            else:
                accidentes = Accidente_Transito.objects.all().filter(Fecha__gte=fechaInicio, Fecha__lte=fechaFin, TipoAccidente=TipoAccidente)
                contador = Accidente_Transito.objects.filter(Fecha__gte=fechaInicio, Fecha__lte=fechaFin, TipoAccidente=TipoAccidente).count()
            
            return render(request, 'Gestionar_Accidente/crear_accidente_transito_juez.html', {'accidentes': accidentes, 'contador': contador})
        except Accidente_Transito.DoesNotExist:
            messages.warning(request, 'No se encontraron coincidencias')
            return render(request, 'Gestionar_Accidente/crear_accidente_transito_juez.html')

    else:
        messages.warning(request, 'Ingrese NumeroAccidente')
        return render(request, 'Gestionar_Accidente/crear_accidente_transito_juez.html')


def buscarAccidente_Transito(request):
    if request.method == 'POST':
        try:
            numeroAccidente = request.POST.get('NumeroAccidente')
            # accidente = Accidente_Transito.objects.all().filter(
            #     NumeroAccidente=request.POST.get('NumeroAccidente'))
            return redirect("/Gestionar_Accidente/detalle_accidente_transito/?NumeroAccidente="+numeroAccidente)
        except Exception as e:
            accidente_transitoForm = Accidente_TransitoForm()
            messages.warning(request, 'Ingrese NumeroAccidente')
            return render(request, 'Gestionar_Accidente/buscar_accidente.html', {'accidente_transitoForm': accidente_transitoForm})

    else:
        accidente_transitoForm = Accidente_TransitoForm()
        return render(request, 'Gestionar_Accidente/buscar_accidente.html', {'accidente_transitoForm': accidente_transitoForm})


def detalleAccidente_Transito(request):
    if request.method == 'POST':
        numeroAccidente = request.POST.get('NumeroAccidente')
        try:
            accidente = Accidente_Transito.objects.get(
                NumeroAccidente=numeroAccidente)
            accidente.Estado = request.POST.get('Estado')
            accidente.save()
            messages.warning(request, 'Actualizacion correcta')
            return redirect('/Gestionar_Accidente/bucar_accidente_transito/')

        except Exception as e:
            accidente_transitoForm = Accidente_TransitoForm()
            messages.warning(request, 'Numero Incorrecto')
            return redirect('/Gestionar_Accidente/bucar_accidente_transito/')

    else:
        try:
            accidente = Accidente_Transito.objects.all().filter(
                NumeroAccidente=request.GET['NumeroAccidente'])
            accidente_transitoForm = Accidente_TransitoForm()
            contex = {
                'accidente': accidente,
                'accidente_transitoForm': accidente_transitoForm
            }
            return render(request, 'Gestionar_Accidente/formulario_accidente.html', contex)
        except Exception as e:
            messages.warning(request, 'Numero Incorrecto')
            accidente_transitoForm = Accidente_TransitoForm()
            return redirect('/Gestionar_Accidente/bucar_accidente_transito/')


def mapaAccidente(request):
    if request.method == 'GET':
        id = request.GET['Accidente_Transito']
        accidente = Accidente_Transito.objects.all().filter(NumeroAccidente=id)

    context = {'accidente': accidente,
               }
    return render(request, 'Gestionar_Accidente/mapaAccidente.html', context)


def Reportesadicionara(request):
    if request.method == 'POST':
        id = request.GET['Accidente_Transito']

        foto = MyImage()
        foto.model_pic = request.POST.get('model_pic')
        foto.id_Evidencia = request.GET['Accidente_Transito']
        if foto.model_pic != '':
            foto.model_pic = request.FILES.get('model_pic')
            foto.save()

        audio = MyAudio()
        audio.model_aud = request.POST.get('model_aud')
        audio.id_Evidencia = request.GET['Accidente_Transito']
        if audio.model_aud != '':
            audio.model_aud = request.FILES.get('model_aud')
            audio.save()

        video = MyVideo()
        video.model_vid = request.POST.get('model_vid')
        video.id_Evidencia = request.GET['Accidente_Transito']
        if video.model_vid != '':
            video.model_vid = request.FILES.get('model_vid')
            video.save()

        messages.warning(request, 'Actualizacion correcta')
        return redirect('/Gestionar_Accidente/crear_accidente_transito/')
    else:
        accidente_form = Accidente_TransitoForm()
        audform = audioform(request.POST, request.FILES)
        vidform = videoform(request.POST, request.FILES)
        fotoform = imageform(request.POST, request.FILES)
        id = request.GET['Accidente_Transito']
        accidente = Accidente_Transito.objects.all().filter(NumeroAccidente=id)
        context = {'accidente': accidente, 'accidente_form': accidente_form,
                   'audform': audform, 'vidform': vidform, 'fotoform': fotoform}
        return render(request, 'Gestionar_Accidente/reportesa.html', context)


def apinindex(request):
    try:
        id = request.GET['Accidente_Transito']
        accidente = Accidente_Transito.objects.all().filter(NumeroAccidente=id)
        context = {'accidente': accidente}
        messages.warning(request, 'Actualizacion correcta')
        return render(request, 'Gestionar_Accidente/accidentepin.html', context)

    except Exception as e:
        messages.warning(request, 'Actualizacion correcta')
        return redirect('/index/')


import io
import matplotlib.pyplot as plt

from django.http import HttpResponse
from django.shortcuts import render
from matplotlib.backends.backend_agg import FigureCanvasAgg
from random import sample


def plot(request):

    
        #Enero
        fechaInicioe = str('2019-1-1')
        datese = datetime.datetime.strptime(fechaInicioe, '%Y-%m-%d').date()
        fechaFine = datese + datetime.timedelta(days=30)
        #Febrero
        fechaIniciof = str('2019-2-1')
        datesf = datetime.datetime.strptime(fechaIniciof, '%Y-%m-%d').date()
        fechaFinf = datesf + datetime.timedelta(days=30)
        #Marzo
        fechaIniciom = str('2019-3-1')
        datesm = datetime.datetime.strptime(fechaIniciom, '%Y-%m-%d').date()
        fechaFinm = datesm + datetime.timedelta(days=30)
        #abril
        fechaInicioa = str('2019-4-1')
        datesa = datetime.datetime.strptime(fechaInicioa, '%Y-%m-%d').date()
        fechaFina = datesa + datetime.timedelta(days=30)
        #mayo
        fechaIniciomy = str('2019-5-1')
        datesmy = datetime.datetime.strptime(fechaIniciomy, '%Y-%m-%d').date()
        fechaFinmy = datesmy + datetime.timedelta(days=30)
        #junio
        fechaIniciojn = str('2019-6-1')
        datesjn = datetime.datetime.strptime(fechaIniciojn, '%Y-%m-%d').date()
        fechaFinjn = datesjn + datetime.timedelta(days=30)
        #julio
        fechaIniciojl = str('2019-7-1')
        datesjl = datetime.datetime.strptime(fechaIniciojl, '%Y-%m-%d').date()
        fechaFinjl = datesjl + datetime.timedelta(days=30)
        #agosto
        fechaInicioag = str('2019-8-1')
        datesag = datetime.datetime.strptime(fechaInicioag, '%Y-%m-%d').date()
        fechaFinag = datesag + datetime.timedelta(days=30)
        #septiembre
        fechaInicios = str('2019-9-1')
        datess = datetime.datetime.strptime(fechaInicios, '%Y-%m-%d').date()
        fechaFins = datess + datetime.timedelta(days=30)
        #octubre
        fechaInicioo = str('2019-10-1')
        dateso = datetime.datetime.strptime(fechaInicioo, '%Y-%m-%d').date()
        fechaFino = dateso + datetime.timedelta(days=30)
        #noviembre
        fechaInicion = str('2019-11-1')
        datesn = datetime.datetime.strptime(fechaInicion, '%Y-%m-%d').date()
        fechaFinn = datesn + datetime.timedelta(days=30)
        #diciembre
        fechaIniciod = str('2019-12-1')
        datesd = datetime.datetime.strptime(fechaIniciod, '%Y-%m-%d').date()
        fechaFind = datesd + datetime.timedelta(days=30)

    

        enero = Accidente_Transito.objects.filter(Fecha__gte=datese, Fecha__lte=fechaFine).count()
        febrero = Accidente_Transito.objects.filter(Fecha__gte=datesf, Fecha__lte=fechaFinf).count()
        marzo = Accidente_Transito.objects.filter(Fecha__gte=datesm, Fecha__lte=fechaFinm).count()
        abril = Accidente_Transito.objects.filter(Fecha__gte=datesa, Fecha__lte=fechaFina).count()
        mayo = Accidente_Transito.objects.filter(Fecha__gte=datesmy, Fecha__lte=fechaFinmy).count()
        junio = Accidente_Transito.objects.filter(Fecha__gte=datesjn, Fecha__lte=fechaFinjn).count()
        julio = Accidente_Transito.objects.filter(Fecha__gte=datesjl, Fecha__lte=fechaFinjl).count()
        agosto = Accidente_Transito.objects.filter(Fecha__gte=datesag, Fecha__lte=fechaFinag).count()
        septiembre = Accidente_Transito.objects.filter(Fecha__gte=datess, Fecha__lte=fechaFins).count()
        octubre = Accidente_Transito.objects.filter(Fecha__gte=dateso, Fecha__lte=fechaFino).count()
        noviembre = Accidente_Transito.objects.filter(Fecha__gte=datesn, Fecha__lte=fechaFinn).count()
        diciembre = Accidente_Transito.objects.filter(Fecha__gte=datesd, Fecha__lte=fechaFind).count()

        x = [1,2,3,4,5,6,7,8,9,10,11,12]
        y = [int(enero),int(febrero),int(marzo),int(abril),int(mayo),int(junio),int(julio),int(agosto),int(septiembre),int(octubre),int(noviembre),int(diciembre)]

        # Creamos una figura y le dibujamos el gráfico
        f = plt.figure()

        # Creamos los ejes
        axes = f.add_axes([0.15, 0.15, 0.75, 0.75]) # [left, bottom, width, height]
        axes.bar(x,y, color = "r")
        axes.plot(x,y, marker='o', linestyle=':', color='b')
        axes.set_xlabel("Meses")
        axes.set_ylabel("Incidencias")
        axes.set_title("GRAFICO 2019")
        axes.grid(True)

        # Como enviaremos la imagen en bytes la guardaremos en un buffer
        buf = io.BytesIO()
        canvas = FigureCanvasAgg(f)
        canvas.print_png(buf)

        # Creamos la respuesta enviando los bytes en tipo imagen png
        response = HttpResponse(buf.getvalue(), content_type='image/png')

        # Limpiamos la figura para liberar memoria
        f.clear()

        # Añadimos la cabecera de longitud de fichero para más estabilidad
        response['Content-Length'] = str(len(response.content))

        # Devolvemos la response
        return response



def ploter(request):
    # Anio 2019
    #Enero
        fechaInicioe = str('2019-1-1')
        datese = datetime.datetime.strptime(fechaInicioe, '%Y-%m-%d').date()
        fechaFine = datese + datetime.timedelta(days=30)
        #Febrero
        fechaIniciof = str('2019-2-1')
        datesf = datetime.datetime.strptime(fechaIniciof, '%Y-%m-%d').date()
        fechaFinf = datesf + datetime.timedelta(days=30)
        #Marzo
        fechaIniciom = str('2019-3-1')
        datesm = datetime.datetime.strptime(fechaIniciom, '%Y-%m-%d').date()
        fechaFinm = datesm + datetime.timedelta(days=30)
        #abril
        fechaInicioa = str('2019-4-1')
        datesa = datetime.datetime.strptime(fechaInicioa, '%Y-%m-%d').date()
        fechaFina = datesa + datetime.timedelta(days=30)
        #mayo
        fechaIniciomy = str('2019-5-1')
        datesmy = datetime.datetime.strptime(fechaIniciomy, '%Y-%m-%d').date()
        fechaFinmy = datesmy + datetime.timedelta(days=30)
        #junio
        fechaIniciojn = str('2019-6-1')
        datesjn = datetime.datetime.strptime(fechaIniciojn, '%Y-%m-%d').date()
        fechaFinjn = datesjn + datetime.timedelta(days=30)
        #julio
        fechaIniciojl = str('2019-7-1')
        datesjl = datetime.datetime.strptime(fechaIniciojl, '%Y-%m-%d').date()
        fechaFinjl = datesjl + datetime.timedelta(days=30)
        #agosto
        fechaInicioag = str('2019-8-1')
        datesag = datetime.datetime.strptime(fechaInicioag, '%Y-%m-%d').date()
        fechaFinag = datesag + datetime.timedelta(days=30)
        #septiembre
        fechaInicios = str('2019-9-1')
        datess = datetime.datetime.strptime(fechaInicios, '%Y-%m-%d').date()
        fechaFins = datess + datetime.timedelta(days=30)
        #octubre
        fechaInicioo = str('2019-10-1')
        dateso = datetime.datetime.strptime(fechaInicioo, '%Y-%m-%d').date()
        fechaFino = dateso + datetime.timedelta(days=30)
        #noviembre
        fechaInicion = str('2019-11-1')
        datesn = datetime.datetime.strptime(fechaInicion, '%Y-%m-%d').date()
        fechaFinn = datesn + datetime.timedelta(days=30)
        #diciembre
        fechaIniciod = str('2019-12-1')
        datesd = datetime.datetime.strptime(fechaIniciod, '%Y-%m-%d').date()
        fechaFind = datesd + datetime.timedelta(days=30)

    

        enero = Accidente_Transito.objects.filter(Fecha__gte=datese, Fecha__lte=fechaFine).count()
        febrero = Accidente_Transito.objects.filter(Fecha__gte=datesf, Fecha__lte=fechaFinf).count()
        marzo = Accidente_Transito.objects.filter(Fecha__gte=datesm, Fecha__lte=fechaFinm).count()
        abril = Accidente_Transito.objects.filter(Fecha__gte=datesa, Fecha__lte=fechaFina).count()
        mayo = Accidente_Transito.objects.filter(Fecha__gte=datesmy, Fecha__lte=fechaFinmy).count()
        junio = Accidente_Transito.objects.filter(Fecha__gte=datesjn, Fecha__lte=fechaFinjn).count()
        julio = Accidente_Transito.objects.filter(Fecha__gte=datesjl, Fecha__lte=fechaFinjl).count()
        agosto = Accidente_Transito.objects.filter(Fecha__gte=datesag, Fecha__lte=fechaFinag).count()
        septiembre = Accidente_Transito.objects.filter(Fecha__gte=datess, Fecha__lte=fechaFins).count()
        octubre = Accidente_Transito.objects.filter(Fecha__gte=dateso, Fecha__lte=fechaFino).count()
        noviembre = Accidente_Transito.objects.filter(Fecha__gte=datesn, Fecha__lte=fechaFinn).count()
        diciembre = Accidente_Transito.objects.filter(Fecha__gte=datesd, Fecha__lte=fechaFind).count()

        total = enero+febrero+marzo+abril+mayo+junio+julio+agosto+septiembre+octubre+noviembre+diciembre

        context = {
                    'enero': enero,
                    'febrero' : febrero,
                    'marzo' : marzo,
                    'abril' : abril,
                    'mayo' : mayo,
                    'junio' : junio,
                    'julio' : julio,
                    'agosto' : agosto,
                    'septiembre' : septiembre,
                    'octubre' : octubre,
                    'noviembre' : noviembre,
                    'diciembre' : diciembre,
                    'total': total
                }

        return render(request, "Gestionar_Accidente/estadistica2019.html", context)


# anio 2020

def plot2020(request):
    
        #Enero
        fechaInicioe = str('2020-1-1')
        datese = datetime.datetime.strptime(fechaInicioe, '%Y-%m-%d').date()
        fechaFine = datese + datetime.timedelta(days=30)
        #Febrero
        fechaIniciof = str('2020-2-1')
        datesf = datetime.datetime.strptime(fechaIniciof, '%Y-%m-%d').date()
        fechaFinf = datesf + datetime.timedelta(days=30)
        #Marzo
        fechaIniciom = str('2020-3-1')
        datesm = datetime.datetime.strptime(fechaIniciom, '%Y-%m-%d').date()
        fechaFinm = datesm + datetime.timedelta(days=30)
        #abril
        fechaInicioa = str('2020-4-1')
        datesa = datetime.datetime.strptime(fechaInicioa, '%Y-%m-%d').date()
        fechaFina = datesa + datetime.timedelta(days=30)
        #mayo
        fechaIniciomy = str('2020-5-1')
        datesmy = datetime.datetime.strptime(fechaIniciomy, '%Y-%m-%d').date()
        fechaFinmy = datesmy + datetime.timedelta(days=30)
        #junio
        fechaIniciojn = str('2020-6-1')
        datesjn = datetime.datetime.strptime(fechaIniciojn, '%Y-%m-%d').date()
        fechaFinjn = datesjn + datetime.timedelta(days=30)
        #julio
        fechaIniciojl = str('2020-7-1')
        datesjl = datetime.datetime.strptime(fechaIniciojl, '%Y-%m-%d').date()
        fechaFinjl = datesjl + datetime.timedelta(days=30)
        #agosto
        fechaInicioag = str('2020-8-1')
        datesag = datetime.datetime.strptime(fechaInicioag, '%Y-%m-%d').date()
        fechaFinag = datesag + datetime.timedelta(days=30)
        #septiembre
        fechaInicios = str('2020-9-1')
        datess = datetime.datetime.strptime(fechaInicios, '%Y-%m-%d').date()
        fechaFins = datess + datetime.timedelta(days=30)
        #octubre
        fechaInicioo = str('2020-10-1')
        dateso = datetime.datetime.strptime(fechaInicioo, '%Y-%m-%d').date()
        fechaFino = dateso + datetime.timedelta(days=30)
        #noviembre
        fechaInicion = str('2020-11-1')
        datesn = datetime.datetime.strptime(fechaInicion, '%Y-%m-%d').date()
        fechaFinn = datesn + datetime.timedelta(days=30)
        #diciembre
        fechaIniciod = str('2020-12-1')
        datesd = datetime.datetime.strptime(fechaIniciod, '%Y-%m-%d').date()
        fechaFind = datesd + datetime.timedelta(days=30)

    

        enero = Accidente_Transito.objects.filter(Fecha__gte=datese, Fecha__lte=fechaFine).count()
        febrero = Accidente_Transito.objects.filter(Fecha__gte=datesf, Fecha__lte=fechaFinf).count()
        marzo = Accidente_Transito.objects.filter(Fecha__gte=datesm, Fecha__lte=fechaFinm).count()
        abril = Accidente_Transito.objects.filter(Fecha__gte=datesa, Fecha__lte=fechaFina).count()
        mayo = Accidente_Transito.objects.filter(Fecha__gte=datesmy, Fecha__lte=fechaFinmy).count()
        junio = Accidente_Transito.objects.filter(Fecha__gte=datesjn, Fecha__lte=fechaFinjn).count()
        julio = Accidente_Transito.objects.filter(Fecha__gte=datesjl, Fecha__lte=fechaFinjl).count()
        agosto = Accidente_Transito.objects.filter(Fecha__gte=datesag, Fecha__lte=fechaFinag).count()
        septiembre = Accidente_Transito.objects.filter(Fecha__gte=datess, Fecha__lte=fechaFins).count()
        octubre = Accidente_Transito.objects.filter(Fecha__gte=dateso, Fecha__lte=fechaFino).count()
        noviembre = Accidente_Transito.objects.filter(Fecha__gte=datesn, Fecha__lte=fechaFinn).count()
        diciembre = Accidente_Transito.objects.filter(Fecha__gte=datesd, Fecha__lte=fechaFind).count()

        x = [1,2,3,4,5,6,7,8,9,10,11,12]
        y = [int(enero),int(febrero),int(marzo),int(abril),int(mayo),int(junio),int(julio),int(agosto),int(septiembre),int(octubre),int(noviembre),int(diciembre)]

        # Creamos una figura y le dibujamos el gráfico
        f = plt.figure()

        # Creamos los ejes
        axes = f.add_axes([0.15, 0.15, 0.75, 0.75]) # [left, bottom, width, height]
        axes.bar(x,y, color = "r")
        axes.plot(x,y, marker='o', linestyle=':', color='b')
        axes.set_xlabel("Meses")
        axes.set_ylabel("Incidencias")
        axes.set_title("GRAFICO 2020")
        axes.grid(True)

        # Como enviaremos la imagen en bytes la guardaremos en un buffer
        buf = io.BytesIO()
        canvas = FigureCanvasAgg(f)
        canvas.print_png(buf)

        # Creamos la respuesta enviando los bytes en tipo imagen png
        response = HttpResponse(buf.getvalue(), content_type='image/png')

        # Limpiamos la figura para liberar memoria
        f.clear()

        # Añadimos la cabecera de longitud de fichero para más estabilidad
        response['Content-Length'] = str(len(response.content))

        # Devolvemos la response
        return response



def ploter2020(request):
    # Anio 2020
    #Enero
        fechaInicioe = str('2020-1-1')
        datese = datetime.datetime.strptime(fechaInicioe, '%Y-%m-%d').date()
        fechaFine = datese + datetime.timedelta(days=30)
        #Febrero
        fechaIniciof = str('2020-2-1')
        datesf = datetime.datetime.strptime(fechaIniciof, '%Y-%m-%d').date()
        fechaFinf = datesf + datetime.timedelta(days=30)
        #Marzo
        fechaIniciom = str('2020-3-1')
        datesm = datetime.datetime.strptime(fechaIniciom, '%Y-%m-%d').date()
        fechaFinm = datesm + datetime.timedelta(days=30)
        #abril
        fechaInicioa = str('2020-4-1')
        datesa = datetime.datetime.strptime(fechaInicioa, '%Y-%m-%d').date()
        fechaFina = datesa + datetime.timedelta(days=30)
        #mayo
        fechaIniciomy = str('2020-5-1')
        datesmy = datetime.datetime.strptime(fechaIniciomy, '%Y-%m-%d').date()
        fechaFinmy = datesmy + datetime.timedelta(days=30)
        #junio
        fechaIniciojn = str('2020-6-1')
        datesjn = datetime.datetime.strptime(fechaIniciojn, '%Y-%m-%d').date()
        fechaFinjn = datesjn + datetime.timedelta(days=30)
        #julio
        fechaIniciojl = str('2020-7-1')
        datesjl = datetime.datetime.strptime(fechaIniciojl, '%Y-%m-%d').date()
        fechaFinjl = datesjl + datetime.timedelta(days=30)
        #agosto
        fechaInicioag = str('2020-8-1')
        datesag = datetime.datetime.strptime(fechaInicioag, '%Y-%m-%d').date()
        fechaFinag = datesag + datetime.timedelta(days=30)
        #septiembre
        fechaInicios = str('2020-9-1')
        datess = datetime.datetime.strptime(fechaInicios, '%Y-%m-%d').date()
        fechaFins = datess + datetime.timedelta(days=30)
        #octubre
        fechaInicioo = str('2020-10-1')
        dateso = datetime.datetime.strptime(fechaInicioo, '%Y-%m-%d').date()
        fechaFino = dateso + datetime.timedelta(days=30)
        #noviembre
        fechaInicion = str('2020-11-1')
        datesn = datetime.datetime.strptime(fechaInicion, '%Y-%m-%d').date()
        fechaFinn = datesn + datetime.timedelta(days=30)
        #diciembre
        fechaIniciod = str('2020-12-1')
        datesd = datetime.datetime.strptime(fechaIniciod, '%Y-%m-%d').date()
        fechaFind = datesd + datetime.timedelta(days=30)

    

        enero = Accidente_Transito.objects.filter(Fecha__gte=datese, Fecha__lte=fechaFine).count()
        febrero = Accidente_Transito.objects.filter(Fecha__gte=datesf, Fecha__lte=fechaFinf).count()
        marzo = Accidente_Transito.objects.filter(Fecha__gte=datesm, Fecha__lte=fechaFinm).count()
        abril = Accidente_Transito.objects.filter(Fecha__gte=datesa, Fecha__lte=fechaFina).count()
        mayo = Accidente_Transito.objects.filter(Fecha__gte=datesmy, Fecha__lte=fechaFinmy).count()
        junio = Accidente_Transito.objects.filter(Fecha__gte=datesjn, Fecha__lte=fechaFinjn).count()
        julio = Accidente_Transito.objects.filter(Fecha__gte=datesjl, Fecha__lte=fechaFinjl).count()
        agosto = Accidente_Transito.objects.filter(Fecha__gte=datesag, Fecha__lte=fechaFinag).count()
        septiembre = Accidente_Transito.objects.filter(Fecha__gte=datess, Fecha__lte=fechaFins).count()
        octubre = Accidente_Transito.objects.filter(Fecha__gte=dateso, Fecha__lte=fechaFino).count()
        noviembre = Accidente_Transito.objects.filter(Fecha__gte=datesn, Fecha__lte=fechaFinn).count()
        diciembre = Accidente_Transito.objects.filter(Fecha__gte=datesd, Fecha__lte=fechaFind).count()

        total = enero+febrero+marzo+abril+mayo+junio+julio+agosto+septiembre+octubre+noviembre+diciembre

        context = {
                    'enero': enero,
                    'febrero' : febrero,
                    'marzo' : marzo,
                    'abril' : abril,
                    'mayo' : mayo,
                    'junio' : junio,
                    'julio' : julio,
                    'agosto' : agosto,
                    'septiembre' : septiembre,
                    'octubre' : octubre,
                    'noviembre' : noviembre,
                    'diciembre' : diciembre,
                    'total': total
                }

        return render(request, "Gestionar_Accidente/estadistica2020.html", context)



import csv
from django.http import HttpResponse

def exportar_csv(request):
        ano = request.GET['Ano']

#Enero
        fechaInicioe = str(ano+'-1-1')
        datese = datetime.datetime.strptime(fechaInicioe, '%Y-%m-%d').date()
        fechaFine = datese + datetime.timedelta(days=30)
        #Febrero
        fechaIniciof = str(ano+'-2-1')
        datesf = datetime.datetime.strptime(fechaIniciof, '%Y-%m-%d').date()
        fechaFinf = datesf + datetime.timedelta(days=30)
        #Marzo
        fechaIniciom = str(ano+'-3-1')
        datesm = datetime.datetime.strptime(fechaIniciom, '%Y-%m-%d').date()
        fechaFinm = datesm + datetime.timedelta(days=30)
        #abril
        fechaInicioa = str(ano+'-4-1')
        datesa = datetime.datetime.strptime(fechaInicioa, '%Y-%m-%d').date()
        fechaFina = datesa + datetime.timedelta(days=30)
        #mayo
        fechaIniciomy = str(ano+'-5-1')
        datesmy = datetime.datetime.strptime(fechaIniciomy, '%Y-%m-%d').date()
        fechaFinmy = datesmy + datetime.timedelta(days=30)
        #junio
        fechaIniciojn = str(ano+'-6-1')
        datesjn = datetime.datetime.strptime(fechaIniciojn, '%Y-%m-%d').date()
        fechaFinjn = datesjn + datetime.timedelta(days=30)
        #julio
        fechaIniciojl = str(ano+'-7-1')
        datesjl = datetime.datetime.strptime(fechaIniciojl, '%Y-%m-%d').date()
        fechaFinjl = datesjl + datetime.timedelta(days=30)
        #agosto
        fechaInicioag = str(ano+'-8-1')
        datesag = datetime.datetime.strptime(fechaInicioag, '%Y-%m-%d').date()
        fechaFinag = datesag + datetime.timedelta(days=30)
        #septiembre
        fechaInicios = str(ano+'-9-1')
        datess = datetime.datetime.strptime(fechaInicios, '%Y-%m-%d').date()
        fechaFins = datess + datetime.timedelta(days=30)
        #octubre
        fechaInicioo = str(ano+'-10-1')
        dateso = datetime.datetime.strptime(fechaInicioo, '%Y-%m-%d').date()
        fechaFino = dateso + datetime.timedelta(days=30)
        #noviembre
        fechaInicion = str(ano+'-11-1')
        datesn = datetime.datetime.strptime(fechaInicion, '%Y-%m-%d').date()
        fechaFinn = datesn + datetime.timedelta(days=30)
        #diciembre
        fechaIniciod = str(ano+'-12-1')
        datesd = datetime.datetime.strptime(fechaIniciod, '%Y-%m-%d').date()
        fechaFind = datesd + datetime.timedelta(days=30)

    
        #choque
        enero = Accidente_Transito.objects.filter(Fecha__gte=datese, Fecha__lte=fechaFine, TipoAccidente='Choque').count()
        febrero = Accidente_Transito.objects.filter(Fecha__gte=datesf, Fecha__lte=fechaFinf, TipoAccidente='Choque').count()
        marzo = Accidente_Transito.objects.filter(Fecha__gte=datesm, Fecha__lte=fechaFinm, TipoAccidente='Choque').count()
        abril = Accidente_Transito.objects.filter(Fecha__gte=datesa, Fecha__lte=fechaFina, TipoAccidente='Choque').count()
        mayo = Accidente_Transito.objects.filter(Fecha__gte=datesmy, Fecha__lte=fechaFinmy, TipoAccidente='Choque').count()
        junio = Accidente_Transito.objects.filter(Fecha__gte=datesjn, Fecha__lte=fechaFinjn, TipoAccidente='Choque').count()
        julio = Accidente_Transito.objects.filter(Fecha__gte=datesjl, Fecha__lte=fechaFinjl, TipoAccidente='Choque').count()
        agosto = Accidente_Transito.objects.filter(Fecha__gte=datesag, Fecha__lte=fechaFinag, TipoAccidente='Choque').count()
        septiembre = Accidente_Transito.objects.filter(Fecha__gte=datess, Fecha__lte=fechaFins, TipoAccidente='Choque').count()
        octubre = Accidente_Transito.objects.filter(Fecha__gte=dateso, Fecha__lte=fechaFino, TipoAccidente='Choque').count()
        noviembre = Accidente_Transito.objects.filter(Fecha__gte=datesn, Fecha__lte=fechaFinn, TipoAccidente='Choque').count()
        diciembre = Accidente_Transito.objects.filter(Fecha__gte=datesd, Fecha__lte=fechaFind, TipoAccidente='Choque').count()

        #atropellamiento
        enero1 = Accidente_Transito.objects.filter(Fecha__gte=datese, Fecha__lte=fechaFine, TipoAccidente='Atropellamiento').count()
        febrero1 = Accidente_Transito.objects.filter(Fecha__gte=datesf, Fecha__lte=fechaFinf, TipoAccidente='Atropellamiento').count()
        marzo1 = Accidente_Transito.objects.filter(Fecha__gte=datesm, Fecha__lte=fechaFinm, TipoAccidente='Atropellamiento').count()
        abril1 = Accidente_Transito.objects.filter(Fecha__gte=datesa, Fecha__lte=fechaFina, TipoAccidente='Atropellamiento').count()
        mayo1 = Accidente_Transito.objects.filter(Fecha__gte=datesmy, Fecha__lte=fechaFinmy, TipoAccidente='Atropellamiento').count()
        junio1 = Accidente_Transito.objects.filter(Fecha__gte=datesjn, Fecha__lte=fechaFinjn, TipoAccidente='Atropellamiento').count()
        julio1 = Accidente_Transito.objects.filter(Fecha__gte=datesjl, Fecha__lte=fechaFinjl, TipoAccidente='Atropellamiento').count()
        agosto1 = Accidente_Transito.objects.filter(Fecha__gte=datesag, Fecha__lte=fechaFinag, TipoAccidente='Atropellamiento').count()
        septiembre1 = Accidente_Transito.objects.filter(Fecha__gte=datess, Fecha__lte=fechaFins, TipoAccidente='Atropellamiento').count()
        octubre1 = Accidente_Transito.objects.filter(Fecha__gte=dateso, Fecha__lte=fechaFino, TipoAccidente='Atropellamiento').count()
        noviembre1 = Accidente_Transito.objects.filter(Fecha__gte=datesn, Fecha__lte=fechaFinn, TipoAccidente='Atropellamiento').count()
        diciembre1 = Accidente_Transito.objects.filter(Fecha__gte=datesd, Fecha__lte=fechaFind, TipoAccidente='Atropellamiento').count()

        #volcamiento
        enero2 = Accidente_Transito.objects.filter(Fecha__gte=datese, Fecha__lte=fechaFine, TipoAccidente='Volcamiento').count()
        febrero2 = Accidente_Transito.objects.filter(Fecha__gte=datesf, Fecha__lte=fechaFinf, TipoAccidente='Volcamiento').count()
        marzo2 = Accidente_Transito.objects.filter(Fecha__gte=datesm, Fecha__lte=fechaFinm, TipoAccidente='Volcamiento').count()
        abril2 = Accidente_Transito.objects.filter(Fecha__gte=datesa, Fecha__lte=fechaFina, TipoAccidente='Volcamiento').count()
        mayo2 = Accidente_Transito.objects.filter(Fecha__gte=datesmy, Fecha__lte=fechaFinmy, TipoAccidente='Volcamiento').count()
        junio2 = Accidente_Transito.objects.filter(Fecha__gte=datesjn, Fecha__lte=fechaFinjn, TipoAccidente='Volcamiento').count()
        julio2 = Accidente_Transito.objects.filter(Fecha__gte=datesjl, Fecha__lte=fechaFinjl, TipoAccidente='Volcamiento').count()
        agosto2 = Accidente_Transito.objects.filter(Fecha__gte=datesag, Fecha__lte=fechaFinag, TipoAccidente='Volcamiento').count()
        septiembre2 = Accidente_Transito.objects.filter(Fecha__gte=datess, Fecha__lte=fechaFins, TipoAccidente='Volcamiento').count()
        octubre2 = Accidente_Transito.objects.filter(Fecha__gte=dateso, Fecha__lte=fechaFino, TipoAccidente='Volcamiento').count()
        noviembre2 = Accidente_Transito.objects.filter(Fecha__gte=datesn, Fecha__lte=fechaFinn, TipoAccidente='Volcamiento').count()
        diciembre2 = Accidente_Transito.objects.filter(Fecha__gte=datesd, Fecha__lte=fechaFind, TipoAccidente='Volcamiento').count()

        #caida del ocupante
        enero3 = Accidente_Transito.objects.filter(Fecha__gte=datese, Fecha__lte=fechaFine, TipoAccidente='Caida del ocupante').count()
        febrero3 = Accidente_Transito.objects.filter(Fecha__gte=datesf, Fecha__lte=fechaFinf, TipoAccidente='Caida del ocupante').count()
        marzo3 = Accidente_Transito.objects.filter(Fecha__gte=datesm, Fecha__lte=fechaFinm, TipoAccidente='Caida del ocupante').count()
        abril3 = Accidente_Transito.objects.filter(Fecha__gte=datesa, Fecha__lte=fechaFina, TipoAccidente='Caida del ocupante').count()
        mayo3 = Accidente_Transito.objects.filter(Fecha__gte=datesmy, Fecha__lte=fechaFinmy, TipoAccidente='Caida del ocupante').count()
        junio3 = Accidente_Transito.objects.filter(Fecha__gte=datesjn, Fecha__lte=fechaFinjn, TipoAccidente='Caida del ocupante').count()
        julio3 = Accidente_Transito.objects.filter(Fecha__gte=datesjl, Fecha__lte=fechaFinjl, TipoAccidente='Caida del ocupante').count()
        agosto3 = Accidente_Transito.objects.filter(Fecha__gte=datesag, Fecha__lte=fechaFinag, TipoAccidente='Caida del ocupante').count()
        septiembre3 = Accidente_Transito.objects.filter(Fecha__gte=datess, Fecha__lte=fechaFins, TipoAccidente='Caida del ocupante').count()
        octubre3 = Accidente_Transito.objects.filter(Fecha__gte=dateso, Fecha__lte=fechaFino, TipoAccidente='Caida del ocupante').count()
        noviembre3 = Accidente_Transito.objects.filter(Fecha__gte=datesn, Fecha__lte=fechaFinn, TipoAccidente='Caida del ocupante').count()
        diciembre3 = Accidente_Transito.objects.filter(Fecha__gte=datesd, Fecha__lte=fechaFind, TipoAccidente='Caida del ocupante').count()

        #incendio
        enero4 = Accidente_Transito.objects.filter(Fecha__gte=datese, Fecha__lte=fechaFine, TipoAccidente='Incendio').count()
        febrero4 = Accidente_Transito.objects.filter(Fecha__gte=datesf, Fecha__lte=fechaFinf, TipoAccidente='Incendio').count()
        marzo4 = Accidente_Transito.objects.filter(Fecha__gte=datesm, Fecha__lte=fechaFinm, TipoAccidente='Incendio').count()
        abril4 = Accidente_Transito.objects.filter(Fecha__gte=datesa, Fecha__lte=fechaFina, TipoAccidente='Incendio').count()
        mayo4 = Accidente_Transito.objects.filter(Fecha__gte=datesmy, Fecha__lte=fechaFinmy, TipoAccidente='Incendio').count()
        junio4 = Accidente_Transito.objects.filter(Fecha__gte=datesjn, Fecha__lte=fechaFinjn, TipoAccidente='Incendio').count()
        julio4 = Accidente_Transito.objects.filter(Fecha__gte=datesjl, Fecha__lte=fechaFinjl, TipoAccidente='Incendio').count()
        agosto4 = Accidente_Transito.objects.filter(Fecha__gte=datesag, Fecha__lte=fechaFinag, TipoAccidente='Incendio').count()
        septiembre4 = Accidente_Transito.objects.filter(Fecha__gte=datess, Fecha__lte=fechaFins, TipoAccidente='Incendio').count()
        octubre4 = Accidente_Transito.objects.filter(Fecha__gte=dateso, Fecha__lte=fechaFino, TipoAccidente='Incendio').count()
        noviembre4 = Accidente_Transito.objects.filter(Fecha__gte=datesn, Fecha__lte=fechaFinn, TipoAccidente='Incendio').count()
        diciembre4 = Accidente_Transito.objects.filter(Fecha__gte=datesd, Fecha__lte=fechaFind, TipoAccidente='Incendio').count()

        #otros
        enero5 = Accidente_Transito.objects.filter(Fecha__gte=datese, Fecha__lte=fechaFine, TipoAccidente='Otros').count()
        febrero5 = Accidente_Transito.objects.filter(Fecha__gte=datesf, Fecha__lte=fechaFinf, TipoAccidente='Otros').count()
        marzo5 = Accidente_Transito.objects.filter(Fecha__gte=datesm, Fecha__lte=fechaFinm, TipoAccidente='Otros').count()
        abril5 = Accidente_Transito.objects.filter(Fecha__gte=datesa, Fecha__lte=fechaFina, TipoAccidente='Otros').count()
        mayo5 = Accidente_Transito.objects.filter(Fecha__gte=datesmy, Fecha__lte=fechaFinmy, TipoAccidente='Otros').count()
        junio5 = Accidente_Transito.objects.filter(Fecha__gte=datesjn, Fecha__lte=fechaFinjn, TipoAccidente='Otros').count()
        julio5 = Accidente_Transito.objects.filter(Fecha__gte=datesjl, Fecha__lte=fechaFinjl, TipoAccidente='Otros').count()
        agosto5 = Accidente_Transito.objects.filter(Fecha__gte=datesag, Fecha__lte=fechaFinag, TipoAccidente='Otros').count()
        septiembre5 = Accidente_Transito.objects.filter(Fecha__gte=datess, Fecha__lte=fechaFins, TipoAccidente='Otros').count()
        octubre5 = Accidente_Transito.objects.filter(Fecha__gte=dateso, Fecha__lte=fechaFino, TipoAccidente='Otros').count()
        noviembre5 = Accidente_Transito.objects.filter(Fecha__gte=datesn, Fecha__lte=fechaFinn, TipoAccidente='Otros').count()
        diciembre5 = Accidente_Transito.objects.filter(Fecha__gte=datesd, Fecha__lte=fechaFind, TipoAccidente='Otros').count()


        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="accidentes.csv"'

        writer = csv.writer(response)
        writer.writerow(['Tipo', 'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre'])
        writer.writerow(['Choque', enero, febrero, marzo, abril, mayo, junio, julio,agosto,septiembre,octubre,noviembre,diciembre])
        writer.writerow(['Atropellamiento', enero1, febrero1, marzo1, abril1, mayo1, junio1, julio1,agosto1,septiembre1,octubre1,noviembre1,diciembre1])
        writer.writerow(['Volcamiento', enero2, febrero2, marzo2, abril2, mayo2, junio2, julio2,agosto2,septiembre2,octubre2,noviembre2,diciembre2])
        writer.writerow(['Caida del ocupante', enero3, febrero3, marzo3, abril3, mayo3, junio3, julio3,agosto3,septiembre3,octubre3,noviembre3,diciembre3])
        writer.writerow(['Incendio', enero4, febrero4, marzo4, abril4, mayo4, junio4, julio4,agosto4,septiembre4,octubre4,noviembre4,diciembre4])
        writer.writerow(['Otros', enero5, febrero5, marzo5, abril5, mayo5, junio5, julio5,agosto5,septiembre5,octubre5,noviembre5,diciembre5])

        return response











# import csv
# from django.http import HttpResponse
# from django.contrib.auth.models import User

# def exportar_csv(request):
#     response = HttpResponse(content_type='text/csv')
#     response['Content-Disposition'] = 'attachment; filename="users.csv"'

#     writer = csv.writer(response)
#     writer.writerow(['Username', 'First name', 'Last name', 'Email address'])

#     users = User.objects.all().values_list('username', 'first_name', 'last_name', 'email')
#     for user in users:
#         writer.writerow(user)

#     return response