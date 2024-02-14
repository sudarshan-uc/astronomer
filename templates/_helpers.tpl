{{- define "logging.indexNamePrefix" -}}
{{- if .Values.global.logging.indexNamePrefix -}}
{{- .Values.global.logging.indexNamePrefix -}}
{{- else -}}
{{- if .Values.global.loggingSidecar.enabled  -}}
vector
{{- else -}}
fluentd
{{- end -}}
{{- end -}}
{{- end -}}


{{ define "houston.internalauthurl" -}}
{{- if .Values.global.enableHoustonInternalAuthorization  }}
nginx.ingress.kubernetes.io/auth-url: http://{{ .Release.Name }}-houston.{{ .Release.Namespace }}.svc.cluster.local:8871/v1/authorization
{{- else }}
nginx.ingress.kubernetes.io/auth-url: https://houston.{{ .Values.global.baseDomain }}/v1/authorization
{{- end }}
{{- end }}

{{ define "authSidecar.image" -}}
{{- if .Values.global.privateRegistry.enabled -}}
{{ .Values.global.privateRegistry.repository }}/ap-auth-sidecar:{{ .Values.global.authSidecar.tag }}
{{- else -}}
{{ .Values.global.authSidecar.repository }}:{{ .Values.global.authSidecar.tag }}
{{- end }}
{{- end }}

{{ define "loggingSidecar.image" -}}
{{- if .Values.global.privateRegistry.enabled -}}
{{ .Values.global.privateRegistry.repository }}/ap-vector:{{ (splitList ":"  .Values.global.loggingSidecar.image ) | last  }}
{{- else -}}
{{ .Values.global.loggingSidecar.image }}
{{- end }}
{{- end }}

{{ define "certCopier.image" -}}
{{- if .Values.global.privateRegistry.enabled -}}
{{ .Values.global.privateRegistry.repository }}/ap-base:{{ .Values.global.privateCaCertsAddToHost.certCopier.tag }}
{{- else -}}
{{ .Values.global.privateCaCertsAddToHost.certCopier.repository }}:{{ .Values.global.privateCaCertsAddToHost.certCopier.tag }}
{{- end }}
{{- end }}

{{/*
Return the proper Docker Image Registry Secret Names
*/}}
{{- define "certCopier.imagePullSecrets" -}}
{{- if and .Values.global.privateRegistry.enabled .Values.global.privateRegistry.secretName }}
imagePullSecrets:
  - name: {{ .Values.global.privateRegistry.secretName }}
{{- end -}}
{{- end -}}
