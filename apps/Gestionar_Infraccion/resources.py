from import_export import resources

from apps.Gestionar_Informacion.models import Conductor, Vehiculo

class ConductorResource(resources.ModelResource):  
   class Meta:  
     model = Conductor  