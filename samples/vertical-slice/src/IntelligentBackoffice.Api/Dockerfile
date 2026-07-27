FROM mcr.microsoft.com/dotnet/sdk:10.0 AS build
WORKDIR /src

COPY samples/vertical-slice/src/IntelligentBackoffice.Api/IntelligentBackoffice.Api.csproj .
RUN dotnet restore

COPY samples/vertical-slice/src/IntelligentBackoffice.Api/ .
RUN dotnet publish -c Release -o /app/publish --no-restore /p:UseAppHost=false

FROM mcr.microsoft.com/dotnet/aspnet:10.0 AS runtime
WORKDIR /app
COPY --from=build /app/publish .
EXPOSE 8080
USER $APP_UID
ENTRYPOINT ["dotnet", "IntelligentBackoffice.Api.dll"]
