from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from app_Cliente.models import Documentacion
from app_Credito.models import Credito
from app_User.models import Perfiluser


class HistorialCreditoView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            perfil = Perfiluser.objects.get(usuario=request.user)
        except Perfiluser.DoesNotExist:
            return Response({'error': 'Sin empresa'}, status=status.HTTP_403_FORBIDDEN)
        
        creditos = Credito.objects.filter(empresa=perfil.empresa).select_related('cliente', 'cliente__documentacion', 'cliente__trabajo')
        
        historial = []
        for c in creditos:
            try:
                doc = c.cliente.documentacion
                ci = doc.ci
            except:
                ci = None
                
            try:
                trabajo = c.cliente.trabajo
                cargo = trabajo.cargo
                empresa_trabajo = trabajo.empresa
                salario = trabajo.salario
            except:
                cargo = None
                empresa_trabajo = None
                salario = None
                
            historial.append({
                'ci_cliente': ci,
                'nombre_cliente': c.cliente.nombre,
                'apellido_cliente': c.cliente.apellido,
                'cargo': cargo,
                'empresa_trabajo': empresa_trabajo,
                'salario': salario,
                'monto_prestamo': c.Monto_Solicitado,
                'estado_prestamo': c.enum_estado,
                'moneda': c.Moneda,
            })
        
        return Response(historial)


class HistorialCreditoCIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, ci):
        try:
            perfil = Perfiluser.objects.get(usuario=request.user)
        except Perfiluser.DoesNotExist:
            return Response({'error': 'Sin empresa'}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            doc = Documentacion.objects.get(ci=ci, empresa=perfil.empresa)
            cliente = doc.id_cliente
        except Documentacion.DoesNotExist:
            return Response({'message': 'No se encontraron registros para el CI proporcionado'}, status=status.HTTP_404_NOT_FOUND)
        
        creditos = Credito.objects.filter(cliente=cliente, empresa=perfil.empresa).select_related('cliente', 'cliente__trabajo')
        
        if not creditos.exists():
            return Response({'message': 'No se encontraron créditos para el CI proporcionado'}, status=status.HTTP_404_NOT_FOUND)
        
        historial = []
        for c in creditos:
            try:
                trabajo = cliente.trabajo
                cargo = trabajo.cargo
                empresa_trabajo = trabajo.empresa
                salario = trabajo.salario
            except:
                cargo = None
                empresa_trabajo = None
                salario = None
                
            historial.append({
                'ci_cliente': ci,
                'nombre_cliente': cliente.nombre,
                'apellido_cliente': cliente.apellido,
                'cargo': cargo,
                'empresa_trabajo': empresa_trabajo,
                'salario': salario,
                'monto_prestamo': c.Monto_Solicitado,
                'estado_prestamo': c.enum_estado,
                'moneda': c.Moneda,
            })
        
        return Response(historial)


class EstadoCreditoCIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, ci):
        try:
            perfil = Perfiluser.objects.get(usuario=request.user)
        except Perfiluser.DoesNotExist:
            return Response({'error': 'Sin empresa'}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            doc = Documentacion.objects.get(ci=ci, empresa=perfil.empresa)
            cliente = doc.id_cliente
        except Documentacion.DoesNotExist:
            return Response({'message': 'No se encontraron créditos para el CI proporcionado'}, status=status.HTTP_404_NOT_FOUND)
        
        creditos = Credito.objects.filter(cliente=cliente, empresa=perfil.empresa).order_by('-Fecha_Aprobacion')
        
        if not creditos.exists():
            return Response({'message': 'No se encontraron créditos para el CI proporcionado'}, status=status.HTTP_404_NOT_FOUND)
        
        c = creditos.first()
        return Response([{
            'ci_cliente': ci,
            'nombre_cliente': cliente.nombre,
            'apellido_cliente': cliente.apellido,
            'estado_credito': c.enum_estado,
            'monto': c.Monto_Solicitado,
            'moneda': c.Moneda,
            'fecha_aprobacion': c.Fecha_Aprobacion,
        }])
