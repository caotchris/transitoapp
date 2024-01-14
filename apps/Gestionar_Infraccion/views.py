from django.shortcuts import render, redirect
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.generic.edit import FormView
from django.contrib.auth import login, logout, authenticate
from django.http import HttpResponseRedirect
from django.contrib.auth.forms import AuthenticationForm
from .forms import Articulos_COIPForm, Infraccion_TransitoForm, IntentosForm, ContadorInfForm
from apps.Gestionar_Informacion.forms import ConductorForm, VehiculoForm
from apps.Gestionar_Evidencia.forms import imageform, videoform, audioform
from .models import Infraccion_Transito, Articulos_COIP, Intentos, ContadorInfraccion
from django.views.generic import View, TemplateView, ListView, UpdateView, CreateView, DeleteView
from rest_framework import generics
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from .serializers import ArticulosSerializer, InfraccionSerializer
from apps.Gestionar_Informacion.models import Conductor, Vehiculo
from apps.Gestionar_Evidencia.models import MyImage, MyVideo, MyAudio
from apps.Gestionar_Usuarios.models import Agente_Transito
from apps.Gestionar_Accidente.models import Accidente_Transito
from apps.Gestionar_Usuarios.forms import Agente_Transito_Form

from django.http import JsonResponse
from django.contrib import messages
from django.core.paginator import Paginator
import datetime



from django.http import HttpResponse
from .utils import render_to_pdf #created in step 4
from django.template.loader import get_template

class GeneratePdf(View):
    def get(self, request, *args, **kwargs):
        id = request.GET['Infraccion_Transito']
        infraccion = Infraccion_Transito.objects.all().filter(NumeroInfraccion=id)
        foto = MyImage.objects.all().filter(id_Evidencia=id)
        data = {'hour': datetime.datetime.now(), 'infraccion' : infraccion, 'foto': foto}
        pdf = render_to_pdf('Gestionar_Infraccion/invoice.html', data)
        return HttpResponse(pdf, content_type='application/pdf')


class ArticulosList(generics.ListCreateAPIView):
    queryset = Articulos_COIP.objects.all()
    serializer_class = ArticulosSerializer
    permission_classes = (IsAuthenticated,)
    authentication_class = (TokenAuthentication,)


class InfraccionList(generics.ListCreateAPIView):
    queryset = Infraccion_Transito.objects.all()
    serializer_class = InfraccionSerializer
    permission_classes = (IsAuthenticated,)
    authentication_class = (TokenAuthentication,)


def home(request):
    infracciones = Infraccion_Transito.objects.all()
    accidentes = Accidente_Transito.objects.all()

    fechaInicio = request.POST.get('FechaInicio')
    fechaFin = request.POST.get('FechaFin')
    Tipo = request.POST.get('Tipo')


    if request.method == 'POST':
        if (str(fechaFin)+'' != '') & (str(fechaInicio)+'' != ''):
            try:

                if str(Tipo)+'' == 'Infracciones':
                    infracciones = Infraccion_Transito.objects.all().filter(Fecha_Infraccion__gte=fechaInicio, Fecha_Infraccion__lte=fechaFin)
                    return render(request, 'index.html', {'infracciones': infracciones})

                elif str(Tipo)+'' == 'Accidentes':
                    accidentes = Accidente_Transito.objects.filter(Fecha__gte=fechaInicio, Fecha__lte=fechaFin)
                    return render(request, 'index.html', {'accidentes': accidentes})
                else:
                    accidentes = Accidente_Transito.objects.filter(Fecha__gte=fechaInicio, Fecha__lte=fechaFin)
                    infracciones = Infraccion_Transito.objects.all().filter(Fecha_Infraccion__gte=fechaInicio, Fecha_Infraccion__lte=fechaFin)
                    return render(request, 'index.html', {'infracciones': infracciones, 'accidentes': accidentes})


            except Accidente_Transito.DoesNotExist:
                return render(request, 'index.html', {'infracciones': infracciones, 'accidentes': accidentes})

        else:
            return render(request, 'index.html', {'infracciones': infracciones, 'accidentes': accidentes})

    else:

        for inf in Infraccion_Transito.objects.all().filter(Estado='Reportado'):
            ac = datetime.date.today()
            s = str(inf.Fecha_Registro)

            dates = datetime.datetime.strptime(s, '%Y-%m-%d').date()
            modified_date = dates + datetime.timedelta(days=3)

            if ac >= modified_date:
                inf.Estado = 'Pendiente de pago'
                inf.save()
        return render(request, 'index.html', {'infracciones': infracciones, 'accidentes': accidentes})


def homejuez(request):
    return render(request, 'indexjuez.html')


def redireccionar(request):
    return render(request, 'redireccionar.html')



def crearArticulos_COIP(request):
    if request.method == 'POST':
        print(request.POST)
        articulos_coip_form = Articulos_COIPForm(request.POST)
        if articulos_coip_form.is_valid():
            articulos_coip_form.save()
            messages.warning(request, 'Registro Correcto')
            return redirect('index')
        else:
            messages.warning(request, 'Error en el formulario')
            return render(request, 'Gestionar_Infraccion/crear_articulos_coip.html', {'articulos_coip_form': articulos_coip_form})
    else:
        articulos_coip_form = Articulos_COIPForm()
        return render(request, 'Gestionar_Infraccion/crear_articulos_coip.html', {'articulos_coip_form': articulos_coip_form})


def crearInfraccion_Transito(request):
    if request.method == 'POST':
        infraccion_transito_form = Infraccion_TransitoForm(request.POST)
        articulos_coip_form = Articulos_COIPForm(request.POST)
        conductorform = ConductorForm(request.POST)
        vehiculoform = VehiculoForm(request.POST)
        audform = audioform(request.POST, request.FILES)
        vidform = videoform(request.POST, request.FILES)
        fotoform = imageform(request.POST, request.FILES)
        agenteform = Agente_Transito_Form(request.POST)
        contadorform =ContadorInfForm(request.POST)


        if infraccion_transito_form.is_valid() & articulos_coip_form.is_valid():

            agente = Agente_Transito.objects.get(Cedula=request.POST.get('Cedula'))

            contador = ContadorInfraccion()
            contador.CedulaAgente = request.POST.get('Cedula')
            contador.CodigoAgente = agente.Codigo_Agente
            contador.ContadorAgente = request.POST.get('ContadorInf')
            contador.save()

            agt =Agente_Transito()
            agt.Cedula = request.POST.get('Cedula')
            agt.Nombres = request.POST.get('Nombres')
            agt.Apellidos = request.POST.get('Apellidos')

            articulo = Articulos_COIP()
            articulo.Id_Articulo = request.POST.get('NumeroInfraccion')
            articulo.Articulo = request.POST.get('Articulo')
            articulo.Inciso = request.POST.get('Inciso')
            articulo.Numeral = request.POST.get('Numeral')
            articulo.save()

            cd = Conductor()
            cd.CedulaC = request.POST.get('CedulaC')
            cd.Nombres = request.POST.get('Nombres')
            cd.Apellidos = request.POST.get('Apellidos')
            cd.TipoLicencia = request.POST.get('TipoLicencia')
            cd.CategoriaLicencia = request.POST.get('CategoriaLicencia')
            cd.FechaEmisionLicencia= request.POST.get('FechaEmisionLicencia')
            cd.FechaCaducidadLicencia = request.POST.get('FechaCaducidadLicencia')

            vehiculo = Vehiculo()
            vehiculo.Placa = request.POST.get('Placa')
            vehiculo.Marca = request.POST.get('Marca')
            vehiculo.Tipo = request.POST.get('Tipo')
            vehiculo.Color = request.POST.get('Color')
            vehiculo.FechaMatricula = request.POST.get('FechaMatricula')
            vehiculo.FechaCaducidadMatricula = request.POST.get('FechaCaducidadMatricula')

            infraccionT = Infraccion_Transito()
            infraccionT.NumeroInfraccion = request.POST.get('NumeroInfraccion')
            infraccionT.Descripcion = request.POST.get('Descripcion')
            infraccionT.Ubicacion = request.POST.get('Ubicacion')
            infraccionT.Latitud = request.POST.get('Latitud')
            infraccionT.Longitud = request.POST.get('Longitud')
            infraccionT.Estado = request.POST.get('Estado')
            infraccionT.Fecha_Infraccion = request.POST.get('Fecha_Infraccion')
            infraccionT.Hora_Infraccion = request.POST.get('Hora_Infraccion')
            infraccionT.Hora_Detencion = request.POST.get('Hora_Detencion')
            infraccionT.Agente = agt
            infraccionT.ArticuloC = articulo
            infraccionT.Conductor = cd
            infraccionT.Vehiculo = vehiculo
            infraccionT.save()

            foto = MyImage()
            foto.model_pic = request.POST.get('model_pic')
            foto.id_Evidencia = request.POST.get('NumeroInfraccion')
            if foto.model_pic != '':
                foto.model_pic = request.FILES.get('model_pic')
                foto.save()

            audio = MyAudio()
            audio.model_aud = request.POST.get('model_aud')
            audio.id_Evidencia = request.POST.get('NumeroInfraccion')
            if audio.model_aud != '':
                audio.model_aud = request.FILES.get('model_aud')
                audio.save()

            video = MyVideo()
            video.model_vid = request.POST.get('model_vid')
            video.id_Evidencia = request.POST.get('NumeroInfraccion')
            if video.model_vid != '':
                video.model_vid = request.FILES.get('model_vid')
                video.save()

            messages.warning(request, 'Registro Correcto')
            return redirect('index')  # retorno de confirmacion
        else:
            messages.warning(request, 'Error en el formulario')
            return render(request,'Gestionar_Infraccion/crear_infraccion_transito.html',{'infraccion_transito_form':infraccion_transito_form, 'articulos_coip_form':articulos_coip_form, 'conductorform':conductorform, 'vehiculoform':vehiculoform, 'audform': audform, 'vidform': vidform, 'fotoform': fotoform, 'contadorform':contadorform, 'agenteform': agenteform})
    else:
        infraccion_transito_form = Infraccion_TransitoForm()
        articulos_coip_form = Articulos_COIPForm()
        conductorform = ConductorForm()
        vehiculoform = VehiculoForm()
        agenteform = Agente_Transito_Form()
        audform = audioform(request.POST, request.FILES)
        vidform = videoform(request.POST, request.FILES)
        fotoform = imageform(request.POST, request.FILES)
        contadorform =ContadorInfForm()
        messages.warning(request, 'Error')
        return render(request, 'Gestionar_Infraccion/crear_infraccion_transito.html', {'infraccion_transito_form': infraccion_transito_form, 'articulos_coip_form': articulos_coip_form, 'conductorform': conductorform, 'vehiculoform': vehiculoform, 'agenteform': agenteform, 'audform': audform, 'vidform': vidform, 'fotoform': fotoform})


def buscar_InfraccionNumAgente(request):
    if request.method == 'POST':
        codAgente = request.POST.get('Codigo_Agente')
        try:
            agente = Agente_Transito.objects.get(Codigo_Agente=codAgente)
        except Exception as e:
            raise e


def listarInfraccion(request):
    infracciones = Infraccion_Transito.objects.all()
    NumeroInfraccion = 0  # filtro por defecto
    if request.POST.get('NumeroInfraccion'):
        NumeroInfraccion = int(request.POST.get('NumeroInfraccion'))
        infracciones = infracciones.filter(
            NumeroInfraccion__gte=NumeroInfraccion)
    return render(request, 'Gestionar_Infraccion/listar_infraccion_transito.html', {'infracciones': infracciones, 'NumeroInfraccion': NumeroInfraccion})


def buscar_intentos(request):
    fechaInicio = request.POST.get('FechaInicio')
    fechaFin = request.POST.get('FechaFin')
    intentos = Intentos.objects.filter(Accion=0)
    Cedula = ''  # filtro por defecto
    intentoform = IntentosForm()
    intentoform = IntentosForm(request.POST)
    if request.POST.get('Cedula'):
        Cedula = int(request.POST.get('Cedula'))
        intentos = intentos.filter(Cedula=Cedula)

    if request.method == 'POST':
       if (str(fechaInicio)+'' != '') & (str(fechaFin)+'' != ''):
              intentos = intentos.filter(Fecha_Intento__gte=str(fechaInicio), Fecha_Intento__lte=str(fechaFin))

    return render(request, 'Gestionar_Infraccion/consultaIntentos.html', {'intentos': intentos, 'Cedula': Cedula, 'intentoform': intentoform})



def buscar_infracciones(request):
    if request.method == 'POST':
        numeroInfraccion = request.POST.get('NumeroInfraccion')
        fechaInicio = request.POST.get('FechaInicio')
        fechaFin = request.POST.get('FechaFin')
        conductor = request.POST.get('Conductor')
        vehiculo = request.POST.get('Vehiculo')
        estado = request.POST.get('Estado')
        Tipo = request.POST.get('Tipo')

        if (str(numeroInfraccion) != ''):
            try:
                infraccion = Infraccion_Transito.objects.all().filter(NumeroInfraccion=numeroInfraccion)
                contador = Infraccion_Transito.objects.all().filter(NumeroInfraccion=numeroInfraccion).count()
                context = {
                    'infraccion': infraccion,
                    'contador' : contador,
                }
                

                return render(request, 'Gestionar_Infraccion/consultaInfraccion.html', context)
            except Exception as e:
                messages.warning(request, "No encontrado")
                return render(request, 'Gestionar_Infraccion/consultaInfraccion.html')
        elif (str(fechaInicio) != '') & (str(fechaFin) != ''):
            try:

                if str(Tipo)+'' == 'Todos':
                    infraccion = Infraccion_Transito.objects.all().filter(Fecha_Infraccion__gte=fechaInicio, Fecha_Infraccion__lte=fechaFin)
                    contador = Infraccion_Transito.objects.all().filter(Fecha_Infraccion__gte=fechaInicio, Fecha_Infraccion__lte=fechaFin).count()
                    context = {
                        'infraccion': infraccion,
                        'contador' : contador,
                    }
                else:
                    infraccion = Infraccion_Transito.objects.all().filter(Fecha_Infraccion__gte=fechaInicio, Fecha_Infraccion__lte=fechaFin, ArticuloC__Articulo__icontains=Tipo)
                    contador = Infraccion_Transito.objects.all().filter(Fecha_Infraccion__gte=fechaInicio, Fecha_Infraccion__lte=fechaFin, ArticuloC__Articulo__icontains=Tipo).count()
                    context = {
                        'infraccion': infraccion,
                        'contador' : contador,
                    }

                return render(request, 'Gestionar_Infraccion/consultaInfraccion.html', context)
            except Exception as e:
                messages.warning(request, "No encontrado")
                return render(request, 'Gestionar_Infraccion/consultaInfraccion.html')

        elif (str(conductor) != ''):
            try:
                infraccion = Infraccion_Transito.objects.all().filter(Conductor=conductor)
                contador = Infraccion_Transito.objects.all().filter(Conductor=conductor).count()
                context = {
                    'infraccion': infraccion,
                    'contador' : contador,
                }
                return render(request, 'Gestionar_Infraccion/consultaInfraccion.html', context)
            except Exception as e:
                messages.warning(request, "No encontrado")
                return render(request, 'Gestionar_Infraccion/consultaInfraccion.html')

        elif (str(vehiculo) != ''):
            try:
                infraccion = Infraccion_Transito.objects.all().filter(Vehiculo=vehiculo)
                contador = Infraccion_Transito.objects.all().filter(Vehiculo=vehiculo).count()
                context = {
                    'infraccion': infraccion,
                    'contador' : contador,
                }
                return render(request, 'Gestionar_Infraccion/consultaInfraccion.html', context)
            except Exception as e:
                messages.warning(request, "No encontrado")
                return render(request, 'Gestionar_Infraccion/consultaInfraccion.html')

        elif (str(estado) != ''):
            try:
                infraccion = Infraccion_Transito.objects.all().filter(Estado=estado)
                contador = Infraccion_Transito.objects.all().filter(Estado=estado).count()
                context = {
                    'infraccion': infraccion,
                    'contador' : contador,
                }
                return render(request, 'Gestionar_Infraccion/consultaInfraccion.html', context)
            except Exception as e:
                messages.warning(request, "No encontrado")
                return render(request, 'Gestionar_Infraccion/consultaInfraccion.html')

        else:
            messages.warning(request, "Ingrese numero")
            return render(request, 'Gestionar_Infraccion/consultaInfraccion.html')
    else:
        return render(request, 'Gestionar_Infraccion/consultaInfraccion.html')


def buscar_infracciones_juez(request):
    if request.method == 'POST':
        numeroInfraccion = request.POST.get('NumeroInfraccion')
        conductor = request.POST.get('Conductor')
        vehiculo = request.POST.get('Vehiculo')

        if (str(numeroInfraccion) != ''):
            try:
                infraccion = Infraccion_Transito.objects.all().filter(NumeroInfraccion=numeroInfraccion)
                contador = Infraccion_Transito.objects.all().filter(NumeroInfraccion=numeroInfraccion).count()
                context = {
                    'infraccion': infraccion,
                    'contador' : contador,
                }
                return render(request, 'Gestionar_Infraccion/consultaInfraccionjuez.html', context)
            except Exception as e:
                messages.warning(request, "No encontrado")
                return render(request, 'Gestionar_Infraccion/consultaInfraccionjuez.html')
        elif (str(conductor) != ''):
            try:
                infraccion = Infraccion_Transito.objects.all().filter(Conductor=conductor)
                contador = Infraccion_Transito.objects.all().filter(Conductor=conductor).count()
                context = {
                    'infraccion': infraccion,
                    'contador' : contador,
                }
                return render(request, 'Gestionar_Infraccion/consultaInfraccionjuez.html', context)
            except Exception as e:
                messages.warning(request, "No encontrado")
                return render(request, 'Gestionar_Infraccion/consultaInfraccionjuez.html')

        elif (str(vehiculo) != ''):
            try:
                infraccion = Infraccion_Transito.objects.all().filter(Vehiculo=vehiculo)
                contador = Infraccion_Transito.objects.all().filter(Vehiculo=vehiculo).count()
                context = {
                    'infraccion': infraccion,
                    'contador' : contador,
                }
                return render(request, 'Gestionar_Infraccion/consultaInfraccionjuez.html', context)
            except Exception as e:
                messages.warning(request, "No encontrado")
                return render(request, 'Gestionar_Infraccion/consultaInfraccionjuez.html')

        else:
            messages.warning(request, "Ingrese numero")
            return render(request, 'Gestionar_Infraccion/consultaInfraccionjuez.html')
    else:
        return render(request, 'Gestionar_Infraccion/consultaInfraccionjuez.html')


def listarIntento(request):
    id = request.GET['Intentos']
    intentos = Intentos.objects.all().filter(Cedula=id, Accion=1)
    fechaInicio = request.POST.get('FechaInicio')
    fechaFin = request.POST.get('FechaFin')

    context = {'intentos': intentos,}
    return render(request, 'Gestionar_Infraccion/intentoControl.html', context)


def mapaIntento(request):
    if request.method == 'POST':
        id = request.GET['Intentos']
        intentos1 = Intentos.objects.get(id=id)
        intentos1.Descripcion = request.POST.get('Descripcion')
        intentos1.Accion=1
        intentos1.save()
        messages.warning(request, 'Actualizacion correcta')
        return redirect('/Gestionar_Infraccion/buscar_Intentos/')
    else:
        intentoform = IntentosForm()
        id = request.GET['Intentos']
        intentos = Intentos.objects.all().filter(id=id)

        context = {'intentos': intentos,'intentoform': intentoform,}

        return render(request, 'Gestionar_Infraccion/mapaintento.html', context)

def mapaIntentoaccion(request):
    intentoform = IntentosForm()
    id = request.GET['Intentos']
    intentos = Intentos.objects.all().filter(id=id)
    context = {'intentos': intentos,'intentoform': intentoform,}
    return render(request, 'Gestionar_Infraccion/mapaintentoaccion.html', context)


def mapaInfraccion(request):
    if request.method == 'GET':
        id = request.GET['Infraccion_Transito']
        infraccion = Infraccion_Transito.objects.all().filter(NumeroInfraccion=id)

    context = {'infraccion': infraccion,
               }
    return render(request, 'Gestionar_Infraccion/mapaInfraccion.html', context)


def Reportesadicionar(request):
    if request.method == 'POST':
        audform = audioform(request.POST, request.FILES)
        vidform = videoform(request.POST, request.FILES)
        fotoform = imageform(request.POST, request.FILES)
        id = request.GET['Infraccion_Transito']
        infraccion1 = Infraccion_Transito.objects.get(NumeroInfraccion=id)



        if infraccion1.Estado == 'Impugnada':
            infraccion_form = Infraccion_TransitoForm()
            audform = audioform(request.POST, request.FILES)
            vidform = videoform(request.POST, request.FILES)
            fotoform = imageform(request.POST, request.FILES)
            id = request.GET['Infraccion_Transito']
            infraccion = Infraccion_Transito.objects.all().filter(NumeroInfraccion=id)
            context = {'infraccion': infraccion, 'infraccion_form': infraccion_form, 'audform': audform, 'vidform': vidform, 'fotoform': fotoform}
            messages.warning(request, 'No se puede modificar este estado')
            return render(request, 'Gestionar_Infraccion/reportes.html', context)

        if infraccion1.Estado == 'No impugnada':
            messages.warning(request, 'No se puede modificar este estado')
            return render(request, 'Gestionar_Infraccion/reportes.html')

        if infraccion1.Estado == 'Pendiente de pago':
            messages.warning(request, 'No se puede modificar este estado')
            return render(request, 'Gestionar_Infraccion/reportes.html')

        if infraccion1.Estado == 'Pagada':
            messages.warning(request, 'No se puede modificar este estado')
            return render(request, 'Gestionar_Infraccion/reportes.html')


        infraccion1.Estado = request.POST.get('Estado')


        if infraccion1.Estado == 'No impugnada':
            infraccion1.Estado = 'Pendiente de pago'
        infraccion1.save()


        foto = MyImage()
        foto.model_pic = request.POST.get('model_pic')
        foto.id_Evidencia = request.GET['Infraccion_Transito']
        if foto.model_pic != '':
            foto.model_pic = request.FILES.get('model_pic')
            foto.save()

        audio = MyAudio()
        audio.model_aud = request.POST.get('model_aud')
        audio.id_Evidencia = request.GET['Infraccion_Transito']
        if audio.model_aud != '':
            audio.model_aud = request.FILES.get('model_aud')
            audio.save()

        video = MyVideo()
        video.model_vid = request.POST.get('model_vid')
        video.id_Evidencia = request.GET['Infraccion_Transito']
        if video.model_vid != '':
            video.model_vid = request.FILES.get('model_vid')
            video.save()

        messages.warning(request, 'Actualizacion correcta')
        return redirect('/Gestionar_Infraccion/consultar_Infraccion/')
    else:
        infraccion_form = Infraccion_TransitoForm()
        audform = audioform(request.POST, request.FILES)
        vidform = videoform(request.POST, request.FILES)
        fotoform = imageform(request.POST, request.FILES)
        id = request.GET['Infraccion_Transito']
        infraccion = Infraccion_Transito.objects.all().filter(NumeroInfraccion=id)
        context = {'infraccion': infraccion, 'infraccion_form': infraccion_form, 'audform': audform, 'vidform': vidform, 'fotoform': fotoform}
        return render(request, 'Gestionar_Infraccion/reportes.html', context)


def Intento_Transito(request):
    if request.method == 'POST':
        id = request.GET('Intentos')
        try:
            intento = Intentos.objects.all.filter(id=id)
            intento.Descripcion = request.POST.get('Descripcion')
            intento.Accion = 1
            intento.save()
            messages.warning(request, 'Actualizacion correcta')
            return redirect('/Gestionar_Infraccion/buscar_Intentos/')

        except Exception as e:
            accidente_transitoForm = Accidente_TransitoForm()
            messages.warning(request, 'Numero Incorrecto')
            return redirect('/Gestionar_Infraccion/buscar_Intentos/')

def pinindex(request):
    try:
        id = request.GET['Infraccion_Transito']
        infraccion = Infraccion_Transito.objects.all().filter(NumeroInfraccion=id)
        context = {'infraccion': infraccion}
        messages.warning(request, 'Actualizacion correcta')
        return render(request, 'Gestionar_Infraccion/infraccionpin.html', context)

    except Exception as e:
        messages.warning(request, 'Actualizacion correcta')
        return redirect('/index/')





from tablib import Dataset 
from .resources import ConductorResource
 
def importar(request):  
   #template = loader.get_template('export/importar.html')  
   if request.method == 'POST':  
     conductor_resource = ConductorResource()  
     dataset = Dataset()  
     #print(dataset)  
     nuevas_personas = request.FILES['xlsfile']  
     #print(nuevas_personas)  
     imported_data = dataset.load(nuevas_personas.read())  
     #print(dataset)  
     result = conductor_resource.import_data(dataset, dry_run=True) # Test the data import  
     #print(result.has_errors())  
     if not result.has_errors():  
       conductor_resource.import_data(dataset, dry_run=False) # Actually import now  
   return render(request, 'importar.html')  


# Estadistica basica

import io
import matplotlib.pyplot as plt

from django.http import HttpResponse
from django.shortcuts import render
from matplotlib.backends.backend_agg import FigureCanvasAgg

def ploti(request):
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

    

        enero = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datese, Fecha_Infraccion__lte=fechaFine).count()
        febrero = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesf, Fecha_Infraccion__lte=fechaFinf).count()
        marzo = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesm, Fecha_Infraccion__lte=fechaFinm).count()
        abril = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesa, Fecha_Infraccion__lte=fechaFina).count()
        mayo = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesmy, Fecha_Infraccion__lte=fechaFinmy).count()
        junio = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesjn, Fecha_Infraccion__lte=fechaFinjn).count()
        julio = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesjl, Fecha_Infraccion__lte=fechaFinjl).count()
        agosto = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesag, Fecha_Infraccion__lte=fechaFinag).count()
        septiembre = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datess, Fecha_Infraccion__lte=fechaFins).count()
        octubre = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=dateso, Fecha_Infraccion__lte=fechaFino).count()
        noviembre = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesn, Fecha_Infraccion__lte=fechaFinn).count()
        diciembre = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesd, Fecha_Infraccion__lte=fechaFind).count()

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



def ploteri(request):
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

    

        enero = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datese, Fecha_Infraccion__lte=fechaFine).count()
        febrero = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesf, Fecha_Infraccion__lte=fechaFinf).count()
        marzo = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesm, Fecha_Infraccion__lte=fechaFinm).count()
        abril = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesa, Fecha_Infraccion__lte=fechaFina).count()
        mayo = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesmy, Fecha_Infraccion__lte=fechaFinmy).count()
        junio = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesjn, Fecha_Infraccion__lte=fechaFinjn).count()
        julio = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesjl, Fecha_Infraccion__lte=fechaFinjl).count()
        agosto = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesag, Fecha_Infraccion__lte=fechaFinag).count()
        septiembre = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datess, Fecha_Infraccion__lte=fechaFins).count()
        octubre = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=dateso, Fecha_Infraccion__lte=fechaFino).count()
        noviembre = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesn, Fecha_Infraccion__lte=fechaFinn).count()
        diciembre = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesd, Fecha_Infraccion__lte=fechaFind).count()

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

        return render(request, "Gestionar_Infraccion/estadistica2019.html", context)


# anio 2020

def ploti2020(request):
    
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

    

        enero = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datese, Fecha_Infraccion__lte=fechaFine).count()
        febrero = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesf, Fecha_Infraccion__lte=fechaFinf).count()
        marzo = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesm, Fecha_Infraccion__lte=fechaFinm).count()
        abril = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesa, Fecha_Infraccion__lte=fechaFina).count()
        mayo = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesmy, Fecha_Infraccion__lte=fechaFinmy).count()
        junio = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesjn, Fecha_Infraccion__lte=fechaFinjn).count()
        julio = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesjl, Fecha_Infraccion__lte=fechaFinjl).count()
        agosto = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesag, Fecha_Infraccion__lte=fechaFinag).count()
        septiembre = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datess, Fecha_Infraccion__lte=fechaFins).count()
        octubre = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=dateso, Fecha_Infraccion__lte=fechaFino).count()
        noviembre = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesn, Fecha_Infraccion__lte=fechaFinn).count()
        diciembre = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesd, Fecha_Infraccion__lte=fechaFind).count()

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



def ploteri2020(request):
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

    

        enero = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datese, Fecha_Infraccion__lte=fechaFine).count()
        febrero = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesf, Fecha_Infraccion__lte=fechaFinf).count()
        marzo = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesm, Fecha_Infraccion__lte=fechaFinm).count()
        abril = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesa, Fecha_Infraccion__lte=fechaFina).count()
        mayo = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesmy, Fecha_Infraccion__lte=fechaFinmy).count()
        junio = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesjn, Fecha_Infraccion__lte=fechaFinjn).count()
        julio = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesjl, Fecha_Infraccion__lte=fechaFinjl).count()
        agosto = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesag, Fecha_Infraccion__lte=fechaFinag).count()
        septiembre = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datess, Fecha_Infraccion__lte=fechaFins).count()
        octubre = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=dateso, Fecha_Infraccion__lte=fechaFino).count()
        noviembre = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesn, Fecha_Infraccion__lte=fechaFinn).count()
        diciembre = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesd, Fecha_Infraccion__lte=fechaFind).count()

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

        return render(request, "Gestionar_Infraccion/estadistica2020.html", context)



import csv
from django.http import HttpResponse
from django.contrib.auth.models import User

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

    #art 383
    query = 'Art. 383.'
    enero = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datese, Fecha_Infraccion__lte=fechaFine, ArticuloC__Articulo__icontains=query).count()
    febrero = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesf, Fecha_Infraccion__lte=fechaFinf, ArticuloC__Articulo__icontains=query).count()
    marzo = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesm, Fecha_Infraccion__lte=fechaFinm, ArticuloC__Articulo__icontains=query).count()
    abril = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesa, Fecha_Infraccion__lte=fechaFina, ArticuloC__Articulo__icontains=query).count()
    mayo = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesmy, Fecha_Infraccion__lte=fechaFinmy, ArticuloC__Articulo__icontains=query).count()
    junio = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesjn, Fecha_Infraccion__lte=fechaFinjn, ArticuloC__Articulo__icontains=query).count()
    julio = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesjl, Fecha_Infraccion__lte=fechaFinjl, ArticuloC__Articulo__icontains=query).count()
    agosto = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesag, Fecha_Infraccion__lte=fechaFinag, ArticuloC__Articulo__icontains=query).count()
    septiembre = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datess, Fecha_Infraccion__lte=fechaFins, ArticuloC__Articulo__icontains=query).count()
    octubre = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=dateso, Fecha_Infraccion__lte=fechaFino, ArticuloC__Articulo__icontains=query).count()
    noviembre = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesn, Fecha_Infraccion__lte=fechaFinn, ArticuloC__Articulo__icontains=query).count()
    diciembre = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesd, Fecha_Infraccion__lte=fechaFind, ArticuloC__Articulo__icontains=query).count()
    
    #art 384
    query1 = 'Art. 384.'
    enero1 = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datese, Fecha_Infraccion__lte=fechaFine, ArticuloC__Articulo__icontains=query1).count()
    febrero1 = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesf, Fecha_Infraccion__lte=fechaFinf, ArticuloC__Articulo__icontains=query1).count()
    marzo1 = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesm, Fecha_Infraccion__lte=fechaFinm, ArticuloC__Articulo__icontains=query1).count()
    abril1 = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesa, Fecha_Infraccion__lte=fechaFina, ArticuloC__Articulo__icontains=query1).count()
    mayo1 = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesmy, Fecha_Infraccion__lte=fechaFinmy, ArticuloC__Articulo__icontains=query1).count()
    junio1 = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesjn, Fecha_Infraccion__lte=fechaFinjn, ArticuloC__Articulo__icontains=query1).count()
    julio1 = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesjl, Fecha_Infraccion__lte=fechaFinjl, ArticuloC__Articulo__icontains=query1).count()
    agosto1 = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesag, Fecha_Infraccion__lte=fechaFinag, ArticuloC__Articulo__icontains=query1).count()
    septiembre1 = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datess, Fecha_Infraccion__lte=fechaFins, ArticuloC__Articulo__icontains=query1).count()
    octubre1 = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=dateso, Fecha_Infraccion__lte=fechaFino, ArticuloC__Articulo__icontains=query1).count()
    noviembre1 = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesn, Fecha_Infraccion__lte=fechaFinn, ArticuloC__Articulo__icontains=query1).count()
    diciembre1 = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesd, Fecha_Infraccion__lte=fechaFind, ArticuloC__Articulo__icontains=query1).count()

    #art 385
    query2 = 'Art. 385.'
    enero2 = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datese, Fecha_Infraccion__lte=fechaFine, ArticuloC__Articulo__icontains=query2).count()
    febrero2 = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesf, Fecha_Infraccion__lte=fechaFinf, ArticuloC__Articulo__icontains=query2).count()
    marzo2 = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesm, Fecha_Infraccion__lte=fechaFinm, ArticuloC__Articulo__icontains=query2).count()
    abril2 = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesa, Fecha_Infraccion__lte=fechaFina, ArticuloC__Articulo__icontains=query2).count()
    mayo2 = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesmy, Fecha_Infraccion__lte=fechaFinmy, ArticuloC__Articulo__icontains=query2).count()
    junio2 = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesjn, Fecha_Infraccion__lte=fechaFinjn, ArticuloC__Articulo__icontains=query2).count()
    julio2 = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesjl, Fecha_Infraccion__lte=fechaFinjl, ArticuloC__Articulo__icontains=query2).count()
    agosto2 = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesag, Fecha_Infraccion__lte=fechaFinag, ArticuloC__Articulo__icontains=query2).count()
    septiembre2 = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datess, Fecha_Infraccion__lte=fechaFins, ArticuloC__Articulo__icontains=query2).count()
    octubre2 = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=dateso, Fecha_Infraccion__lte=fechaFino, ArticuloC__Articulo__icontains=query2).count()
    noviembre2 = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesn, Fecha_Infraccion__lte=fechaFinn, ArticuloC__Articulo__icontains=query2).count()
    diciembre2 = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesd, Fecha_Infraccion__lte=fechaFind, ArticuloC__Articulo__icontains=query2).count()

    #art 386
    query3 = 'Art. 386.'
    enero3 = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datese, Fecha_Infraccion__lte=fechaFine, ArticuloC__Articulo__icontains=query3).count()
    febrero3 = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesf, Fecha_Infraccion__lte=fechaFinf, ArticuloC__Articulo__icontains=query3).count()
    marzo3 = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesm, Fecha_Infraccion__lte=fechaFinm, ArticuloC__Articulo__icontains=query3).count()
    abril3 = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesa, Fecha_Infraccion__lte=fechaFina, ArticuloC__Articulo__icontains=query3).count()
    mayo3 = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesmy, Fecha_Infraccion__lte=fechaFinmy, ArticuloC__Articulo__icontains=query3).count()
    junio3 = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesjn, Fecha_Infraccion__lte=fechaFinjn, ArticuloC__Articulo__icontains=query3).count()
    julio3 = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesjl, Fecha_Infraccion__lte=fechaFinjl, ArticuloC__Articulo__icontains=query3).count()
    agosto3 = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesag, Fecha_Infraccion__lte=fechaFinag, ArticuloC__Articulo__icontains=query3).count()
    septiembre3 = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datess, Fecha_Infraccion__lte=fechaFins, ArticuloC__Articulo__icontains=query3).count()
    octubre3 = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=dateso, Fecha_Infraccion__lte=fechaFino, ArticuloC__Articulo__icontains=query3).count()
    noviembre3 = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesn, Fecha_Infraccion__lte=fechaFinn, ArticuloC__Articulo__icontains=query3).count()
    diciembre3 = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesd, Fecha_Infraccion__lte=fechaFind, ArticuloC__Articulo__icontains=query3).count()

    #art 387
    query4 = 'Art. 387.'
    enero4 = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datese, Fecha_Infraccion__lte=fechaFine, ArticuloC__Articulo__icontains=query4).count()
    febrero4 = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesf, Fecha_Infraccion__lte=fechaFinf, ArticuloC__Articulo__icontains=query4).count()
    marzo4 = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesm, Fecha_Infraccion__lte=fechaFinm, ArticuloC__Articulo__icontains=query4).count()
    abril4 = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesa, Fecha_Infraccion__lte=fechaFina, ArticuloC__Articulo__icontains=query4).count()
    mayo4 = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesmy, Fecha_Infraccion__lte=fechaFinmy, ArticuloC__Articulo__icontains=query4).count()
    junio4 = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesjn, Fecha_Infraccion__lte=fechaFinjn, ArticuloC__Articulo__icontains=query4).count()
    julio4 = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesjl, Fecha_Infraccion__lte=fechaFinjl, ArticuloC__Articulo__icontains=query4).count()
    agosto4 = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesag, Fecha_Infraccion__lte=fechaFinag, ArticuloC__Articulo__icontains=query4).count()
    septiembre4 = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datess, Fecha_Infraccion__lte=fechaFins, ArticuloC__Articulo__icontains=query4).count()
    octubre4 = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=dateso, Fecha_Infraccion__lte=fechaFino, ArticuloC__Articulo__icontains=query4).count()
    noviembre4 = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesn, Fecha_Infraccion__lte=fechaFinn, ArticuloC__Articulo__icontains=query4).count()
    diciembre4 = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesd, Fecha_Infraccion__lte=fechaFind, ArticuloC__Articulo__icontains=query4).count()

    #art 388
    query5 = 'Art. 388.'
    enero5 = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datese, Fecha_Infraccion__lte=fechaFine, ArticuloC__Articulo__icontains=query5).count()
    febrero5 = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesf, Fecha_Infraccion__lte=fechaFinf, ArticuloC__Articulo__icontains=query5).count()
    marzo5 = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesm, Fecha_Infraccion__lte=fechaFinm, ArticuloC__Articulo__icontains=query5).count()
    abril5 = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesa, Fecha_Infraccion__lte=fechaFina, ArticuloC__Articulo__icontains=query5).count()
    mayo5 = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesmy, Fecha_Infraccion__lte=fechaFinmy, ArticuloC__Articulo__icontains=query5).count()
    junio5 = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesjn, Fecha_Infraccion__lte=fechaFinjn, ArticuloC__Articulo__icontains=query5).count()
    julio5 = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesjl, Fecha_Infraccion__lte=fechaFinjl, ArticuloC__Articulo__icontains=query5).count()
    agosto5 = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesag, Fecha_Infraccion__lte=fechaFinag, ArticuloC__Articulo__icontains=query5).count()
    septiembre5 = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datess, Fecha_Infraccion__lte=fechaFins, ArticuloC__Articulo__icontains=query5).count()
    octubre5 = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=dateso, Fecha_Infraccion__lte=fechaFino, ArticuloC__Articulo__icontains=query5).count()
    noviembre5 = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesn, Fecha_Infraccion__lte=fechaFinn, ArticuloC__Articulo__icontains=query5).count()
    diciembre5 = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesd, Fecha_Infraccion__lte=fechaFind, ArticuloC__Articulo__icontains=query5).count()

    #art 389
    query6 = 'Art. 389.'
    enero6 = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datese, Fecha_Infraccion__lte=fechaFine, ArticuloC__Articulo__icontains=query6).count()
    febrero6 = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesf, Fecha_Infraccion__lte=fechaFinf, ArticuloC__Articulo__icontains=query6).count()
    marzo6 = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesm, Fecha_Infraccion__lte=fechaFinm, ArticuloC__Articulo__icontains=query6).count()
    abril6 = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesa, Fecha_Infraccion__lte=fechaFina, ArticuloC__Articulo__icontains=query6).count()
    mayo6 = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesmy, Fecha_Infraccion__lte=fechaFinmy, ArticuloC__Articulo__icontains=query6).count()
    junio6 = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesjn, Fecha_Infraccion__lte=fechaFinjn, ArticuloC__Articulo__icontains=query6).count()
    julio6 = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesjl, Fecha_Infraccion__lte=fechaFinjl, ArticuloC__Articulo__icontains=query6).count()
    agosto6 = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesag, Fecha_Infraccion__lte=fechaFinag, ArticuloC__Articulo__icontains=query6).count()
    septiembre6 = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datess, Fecha_Infraccion__lte=fechaFins, ArticuloC__Articulo__icontains=query6).count()
    octubre6 = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=dateso, Fecha_Infraccion__lte=fechaFino, ArticuloC__Articulo__icontains=query6).count()
    noviembre6 = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesn, Fecha_Infraccion__lte=fechaFinn, ArticuloC__Articulo__icontains=query6).count()
    diciembre6 = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesd, Fecha_Infraccion__lte=fechaFind, ArticuloC__Articulo__icontains=query6).count()

    #art 390
    query7 = 'Art. 390.'
    enero7 = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datese, Fecha_Infraccion__lte=fechaFine, ArticuloC__Articulo__icontains=query7).count()
    febrero7 = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesf, Fecha_Infraccion__lte=fechaFinf, ArticuloC__Articulo__icontains=query7).count()
    marzo7 = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesm, Fecha_Infraccion__lte=fechaFinm, ArticuloC__Articulo__icontains=query7).count()
    abril7 = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesa, Fecha_Infraccion__lte=fechaFina, ArticuloC__Articulo__icontains=query7).count()
    mayo7 = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesmy, Fecha_Infraccion__lte=fechaFinmy, ArticuloC__Articulo__icontains=query7).count()
    junio7 = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesjn, Fecha_Infraccion__lte=fechaFinjn, ArticuloC__Articulo__icontains=query7).count()
    julio7 = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesjl, Fecha_Infraccion__lte=fechaFinjl, ArticuloC__Articulo__icontains=query7).count()
    agosto7 = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesag, Fecha_Infraccion__lte=fechaFinag, ArticuloC__Articulo__icontains=query7).count()
    septiembre7 = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datess, Fecha_Infraccion__lte=fechaFins, ArticuloC__Articulo__icontains=query7).count()
    octubre7 = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=dateso, Fecha_Infraccion__lte=fechaFino, ArticuloC__Articulo__icontains=query7).count()
    noviembre7 = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesn, Fecha_Infraccion__lte=fechaFinn, ArticuloC__Articulo__icontains=query7).count()
    diciembre7 = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesd, Fecha_Infraccion__lte=fechaFind, ArticuloC__Articulo__icontains=query7).count()

    #art 391
    query8 = 'Art. 391.'
    enero8 = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datese, Fecha_Infraccion__lte=fechaFine, ArticuloC__Articulo__icontains=query8).count()
    febrero8 = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesf, Fecha_Infraccion__lte=fechaFinf, ArticuloC__Articulo__icontains=query8).count()
    marzo8 = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesm, Fecha_Infraccion__lte=fechaFinm, ArticuloC__Articulo__icontains=query8).count()
    abril8 = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesa, Fecha_Infraccion__lte=fechaFina, ArticuloC__Articulo__icontains=query8).count()
    mayo8 = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesmy, Fecha_Infraccion__lte=fechaFinmy, ArticuloC__Articulo__icontains=query8).count()
    junio8 = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesjn, Fecha_Infraccion__lte=fechaFinjn, ArticuloC__Articulo__icontains=query8).count()
    julio8 = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesjl, Fecha_Infraccion__lte=fechaFinjl, ArticuloC__Articulo__icontains=query8).count()
    agosto8 = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesag, Fecha_Infraccion__lte=fechaFinag, ArticuloC__Articulo__icontains=query8).count()
    septiembre8 = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datess, Fecha_Infraccion__lte=fechaFins, ArticuloC__Articulo__icontains=query8).count()
    octubre8 = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=dateso, Fecha_Infraccion__lte=fechaFino, ArticuloC__Articulo__icontains=query8).count()
    noviembre8 = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesn, Fecha_Infraccion__lte=fechaFinn, ArticuloC__Articulo__icontains=query8).count()
    diciembre8 = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesd, Fecha_Infraccion__lte=fechaFind, ArticuloC__Articulo__icontains=query8).count()

    #art 392
    query9 = 'Art. 392.'
    enero9 = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datese, Fecha_Infraccion__lte=fechaFine, ArticuloC__Articulo__icontains=query9).count()
    febrero9 = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesf, Fecha_Infraccion__lte=fechaFinf, ArticuloC__Articulo__icontains=query9).count()
    marzo9 = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesm, Fecha_Infraccion__lte=fechaFinm, ArticuloC__Articulo__icontains=query9).count()
    abril9 = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesa, Fecha_Infraccion__lte=fechaFina, ArticuloC__Articulo__icontains=query9).count()
    mayo9 = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesmy, Fecha_Infraccion__lte=fechaFinmy, ArticuloC__Articulo__icontains=query9).count()
    junio9 = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesjn, Fecha_Infraccion__lte=fechaFinjn, ArticuloC__Articulo__icontains=query9).count()
    julio9 = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesjl, Fecha_Infraccion__lte=fechaFinjl, ArticuloC__Articulo__icontains=query9).count()
    agosto9 = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesag, Fecha_Infraccion__lte=fechaFinag, ArticuloC__Articulo__icontains=query9).count()
    septiembre9 = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datess, Fecha_Infraccion__lte=fechaFins, ArticuloC__Articulo__icontains=query9).count()
    octubre9 = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=dateso, Fecha_Infraccion__lte=fechaFino, ArticuloC__Articulo__icontains=query9).count()
    noviembre9 = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesn, Fecha_Infraccion__lte=fechaFinn, ArticuloC__Articulo__icontains=query9).count()
    diciembre9 = Infraccion_Transito.objects.filter(Fecha_Infraccion__gte=datesd, Fecha_Infraccion__lte=fechaFind, ArticuloC__Articulo__icontains=query9).count()


    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="infracciones.csv"'

    writer = csv.writer(response)
    writer.writerow(['Articulo', 'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre'])
    writer.writerow(['383', enero, febrero, marzo, abril, mayo, junio, julio,agosto,septiembre,octubre,noviembre,diciembre])
    writer.writerow(['384', enero1, febrero1, marzo1, abril1, mayo1, junio1, julio1,agosto1,septiembre1,octubre1,noviembre1,diciembre1])
    writer.writerow(['385', enero2, febrero2, marzo2, abril2, mayo2, junio2, julio2,agosto2,septiembre2,octubre2,noviembre2,diciembre2])
    writer.writerow(['386', enero3, febrero3, marzo3, abril3, mayo3, junio3, julio3,agosto3,septiembre3,octubre3,noviembre3,diciembre3])
    writer.writerow(['387', enero4, febrero4, marzo4, abril4, mayo4, junio4, julio4,agosto4,septiembre4,octubre4,noviembre4,diciembre4])
    writer.writerow(['388', enero5, febrero5, marzo5, abril5, mayo5, junio5, julio5,agosto5,septiembre5,octubre5,noviembre5,diciembre5])
    writer.writerow(['389', enero6, febrero6, marzo6, abril6, mayo6, junio6, julio6,agosto6,septiembre6,octubre6,noviembre6,diciembre6])
    writer.writerow(['390', enero7, febrero7, marzo7, abril7, mayo7, junio7, julio7,agosto7,septiembre7,octubre7,noviembre7,diciembre7])
    writer.writerow(['391', enero8, febrero8, marzo8, abril8, mayo8, junio8, julio8,agosto8,septiembre8,octubre8,noviembre8,diciembre8])
    writer.writerow(['392', enero9, febrero9, marzo9, abril9, mayo9, junio9, julio9,agosto9,septiembre9,octubre9,noviembre9,diciembre9])
    return response